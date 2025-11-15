# backend/app/routers/items.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_ # <--- IMPORT and_ HERE
from app.db.session import get_db
from app.db.models import Item, Category, PriceVariation
# --- IMPORTANT: We need PriceVariationOut to build the response ---
from app.schemas.menu import (
    ItemOut, ItemCreate, ItemUpdate, PriceVariationOut
)
from app.core.embedding import generate_embedding, get_embedding_model
from pgvector.sqlalchemy import Vector
from enum import Enum # Import Enum

# Define Enum for clear search mode options
class SearchMode(str, Enum):
    COMBINED = "combined"
    FTS_ONLY = "fts_only"
    FUZZY_ONLY = "fuzzy_only"

router = APIRouter(prefix="/items", tags=["items"])

# --- ADD THIS HELPER FUNCTION ---
def convert_item_to_item_out(item: Item) -> ItemOut:
    """
    Helper function to manually build the ItemOut model
    and ensure category_name is populated.
    """
    return ItemOut(
        id=item.id,
        category_id=item.category_id,
        subcategory=item.subcategory,
        name=item.name,
        description=item.description,
        is_available=item.is_available,
        # Manually add the category_name
        category_name=item.category.name if item.category else None,
        # Manually validate the variations
        variations=[PriceVariationOut.model_validate(var) for var in item.variations]
    )

# --- UPDATE YOUR TEST ENDPOINT ---
@router.get("/test/{item_id}", response_model=ItemOut)
def test_item_loading(item_id: int, db: Session = Depends(get_db)):
    """
    A minimal endpoint to test relationship loading.
    """
    item_obj = db.query(Item).options(
        joinedload(Item.variations), 
        joinedload(Item.category)
    ).filter(Item.id == item_id).first()

    if not item_obj:
        raise HTTPException(404, "Item not found")

    # --- MANUALLY CONVERT TO ItemOut ---
    return convert_item_to_item_out(item_obj)


@router.get("", response_model=list[ItemOut])
def list_items(
    search: str = Query(None, description="Search query for item name or description."),
    type: str = Query(None, description="Filter by subcategory (e.g., 'veg', 'non-veg')."),
    price_min: float = Query(None, description="Minimum price."),
    price_max: float = Query(None, description="Maximum price."),
    similarity_threshold: float = Query(0.3, description="Similarity threshold for fuzzy search (0 to 1).", ge=0, le=1),
    search_mode: SearchMode = Query(SearchMode.COMBINED, description="Search mode: 'combined' (default), 'fts_only', or 'fuzzy_only'."),
    db: Session = Depends(get_db)
):
    """
    Get menu items with filtering and selectable search modes (FTS, fuzzy, or combined).
    'Combined' mode uses high-precision Per-Word Fuzzy AND logic.
    Falls back to semantic search if no results.
    """
    
    # --- Step 1: Build the base query with filters (price, type) ---
    base_query = db.query(Item.id)
    if type:
        base_query = base_query.filter(func.lower(Item.subcategory) == type.lower())
    if price_min is not None or price_max is not None:
        base_query = base_query.join(Item.variations)
        if price_min is not None:
            base_query = base_query.filter(PriceVariation.final_price >= price_min)
        if price_max is not None:
            base_query = base_query.filter(PriceVariation.final_price <= price_max)

    
    ordered_id_tuples = []

    if search:
        search_term = search.strip()
        
        # --- Step 2: Define all match conditions and scores ---

        # --- FTS definitions (for FTS_ONLY mode) ---
        ts_query = func.plainto_tsquery('simple', search_term)
        fts_match = Item.tsv.op('@@')(ts_query)
        fts_rank = func.ts_rank(Item.tsv, ts_query)
        
        # --- Simple Fuzzy definitions (for FUZZY_ONLY mode) ---
        simple_fuzzy_name_match = func.similarity(Item.name_norm, search_term) > similarity_threshold
        simple_fuzzy_category_match = func.similarity(Item.category_name_norm, search_term) > similarity_threshold
        simple_fuzzy_match = or_(simple_fuzzy_name_match, simple_fuzzy_category_match)
        simple_sim_score = func.greatest(func.similarity(Item.name_norm, search_term), func.similarity(Item.category_name_norm, search_term))

        # --- Step 3: SEARCH LOGIC BASED ON MODE ---

        # Mode 1: FTS_ONLY
        if search_mode == SearchMode.FTS_ONLY:
            print(f"--- Using FTS_ONLY search for '{search}' ---")
            search_query = base_query.filter(fts_match).add_columns(fts_rank).order_by(fts_rank.desc())
            ordered_id_tuples = search_query.distinct().all()

        # Mode 2: FUZZY_ONLY (uses simple, broad fuzzy)
        elif search_mode == SearchMode.FUZZY_ONLY:
            print(f"--- Using FUZZY_ONLY search for '{search}' ---")
            search_query = base_query.filter(simple_fuzzy_match).add_columns(simple_sim_score).order_by(simple_sim_score.desc())
            ordered_id_tuples = search_query.distinct().all()

        # Mode 3: COMBINED (Uses NEW Per-Word AND Fuzzy logic)
        elif search_mode == SearchMode.COMBINED:
            search_words = [word for word in search_term.split() if word]
            num_words = len(search_words)
            
            per_word_fuzzy_match = False
            per_word_sim_score = 0.0

            if num_words > 0:
                # --- Create the AND filter ---
                # All search words must be similar to the name
                name_conditions = [func.similarity(Item.name_norm, word) > similarity_threshold for word in search_words]
                # All search words must be similar to the category
                category_conditions = [func.similarity(Item.category_name_norm, word) > similarity_threshold for word in search_words]
                
                # An item matches if (ALL name words match) OR (ALL category words match)
                per_word_fuzzy_match = or_(
                    and_(*name_conditions),  # <--- FIXED
                    and_(*category_conditions) # <--- FIXED
                )
                
                # --- Create the Ranking Score (Average of similarities) ---
                if num_words > 1:
                    # This generates (sim(word1) + sim(word2) + ...) / num_words
                    avg_name_sim = sum((func.similarity(Item.name_norm, word) for word in search_words), 0.0) / num_words
                    avg_cat_sim = sum((func.similarity(Item.category_name_norm, word) for word in search_words), 0.0) / num_words
                    per_word_sim_score = func.greatest(avg_name_sim, avg_cat_sim)
                else:
                    # Fallback to simple score for single word
                    per_word_sim_score = simple_sim_score
            
            print(f"--- Using Per-Word AND Fuzzy search for '{search}' ---")
            search_query = base_query.filter(per_word_fuzzy_match).add_columns(per_word_sim_score).order_by(per_word_sim_score.desc())
            ordered_id_tuples = search_query.distinct().all()


        # --- Step 4: SEMANTIC FALLBACK (runs if previous search failed) ---
        if not ordered_id_tuples:
            print(f"--- Search for '{search}' empty, falling back to semantic search ---")
            
            model = get_embedding_model() 
            query_embedding = model.encode(search).tolist() 

            distance_col = Item.emb.cosine_distance(query_embedding)
            fallback_query = (
                base_query  
                .add_columns(distance_col)
                .order_by(distance_col.asc()) 
                .distinct()
                .limit(5) 
            )
            ordered_id_tuples = fallback_query.all()

    else:
        # --- Step 5: No search term, just apply default sorting ---
        default_sort_query = base_query.add_columns(Item.name).order_by(Item.name.asc())
        ordered_id_tuples = default_sort_query.distinct().all()


    # --- Step 6: Process results (this part is the same as before) ---
    if not ordered_id_tuples: 
        return []
    
    ordered_ids = [id_tuple[0] for id_tuple in ordered_id_tuples]
    
    items_with_relations = db.query(Item).options(
        joinedload(Item.variations),
        joinedload(Item.category)
    ).filter(
        Item.id.in_(ordered_ids)
    ).all()
    
    items_map = {item.id: item for item in items_with_relations}
    sorted_items = [items_map[item_id] for item_id in ordered_ids if item_id in items_map]

    results = [convert_item_to_item_out(item) for item in sorted_items]
    return results


@router.get("/semantic-search", response_model=list[ItemOut])
def semantic_search_items(
    search: str = Query(..., description="A natural language query."),
    limit: int = Query(5, description="Number of results to return."),
    db: Session = Depends(get_db)
):
    model = get_embedding_model() 
    query_embedding = model.encode(search).tolist() 

    items = db.query(Item).options(
        joinedload(Item.variations),
        joinedload(Item.category) 
    ).order_by(Item.emb.cosine_distance (query_embedding)).limit(limit).all()
    
    # --- MANUALLY CONVERT TO ItemOut ---
    results = [convert_item_to_item_out(item) for item in items]
    return results

# --- POST, PATCH, DELETE Endpoints (Must also be converted) ---
@router.post("", response_model=ItemOut, status_code=201)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    obj = Item(**payload.dict())
    category = db.get(Category, obj.category_id)
    category_name = category.name if category else None
    obj.emb = generate_embedding(payload.dict(), category_name)
    db.add(obj)
    db.commit()
    
    created_item = db.query(Item).options(
        joinedload(Item.variations), 
        joinedload(Item.category)
    ).filter(Item.id == obj.id).first()
    
    # --- MANUALLY CONVERT TO ItemOut ---
    return convert_item_to_item_out(created_item)

@router.patch("/{item_id}", response_model=ItemOut)
def update_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db)):
    obj = db.get(Item, item_id)
    if not obj:
        raise HTTPException(404, "Item not found")

    # ... (update logic is the same) ...
    update_data = payload.dict(exclude_unset=True)
    new_category_id = update_data.get("category_id", obj.category_id)
    for key, value in update_data.items():
        setattr(obj, key, value)
    category = db.get(Category, new_category_id)
    category_name = category.name if category else None
    current_data_for_embedding = {"name": obj.name, "description": obj.description, "subcategory": obj.subcategory}
    obj.emb = generate_embedding(current_data_for_embedding, category_name)
    
    db.commit()

    updated_item = db.query(Item).options(
        joinedload(Item.variations), 
        joinedload(Item.category)
    ).filter(Item.id == item_id).first()

    # --- MANUALLY CONVERT TO ItemOut ---
    return convert_item_to_item_out(updated_item)

@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Item, item_id)
    if not obj:
        raise HTTPException(404, "Item not found")
    db.delete(obj)
    db.commit()