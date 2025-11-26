# backend/app/routers/items.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_
from app.db.session import get_db
from app.db.models import Item, PriceVariation
from app.schemas.menu import ItemOut, ItemCreate, ItemUpdate, PriceVariationOut
from app.core.embedding import generate_embedding, get_embedding_model
from app.db.models import Category 
from enum import Enum
from typing import List, Tuple

# Define Enum for clear search mode options
class SearchMode(str, Enum):
    COMBINED = "combined"
    FTS_ONLY = "fts_only"
    FUZZY_ONLY = "fuzzy_only"

router = APIRouter(prefix="/items", tags=["items"])

def convert_item_to_item_out(item: Item) -> ItemOut:
    return ItemOut(
        id=item.id,
        category_id=item.category_id,
        subcategory=item.subcategory,
        name=item.name,
        description=item.description,
        is_available=item.is_available,
        category_name=item.category.name if item.category else None,
        variations=[PriceVariationOut.model_validate(var) for var in item.variations]
    )


def search_fts(base_query, search_term: str):
    """Performs Full-Text Search using Postgres TSVECTOR."""
    print(f"--- Using FTS_ONLY search for '{search_term}' ---")
    ts_query = func.plainto_tsquery('simple', search_term)
    fts_match = Item.tsv.op('@@')(ts_query)
    fts_rank = func.ts_rank(Item.tsv, ts_query)
    
    return (
        base_query
        .filter(fts_match)
        .add_columns(fts_rank)
        .order_by(fts_rank.desc())
        .distinct()
        .all()
    )

def search_fuzzy(base_query, search_term: str, threshold: float):
    """Performs simple Fuzzy Search on name and category."""
    print(f"--- Using FUZZY_ONLY search for '{search_term}' ---")
    
    name_match = func.similarity(Item.name_norm, search_term) > threshold
    cat_match = func.similarity(Item.category_name_norm, search_term) > threshold
    
    fuzzy_match = or_(name_match, cat_match)
    sim_score = func.greatest(
        func.similarity(Item.name_norm, search_term),
        func.similarity(Item.category_name_norm, search_term)
    )
    
    return (
        base_query
        .filter(fuzzy_match)
        .add_columns(sim_score)
        .order_by(sim_score.desc())
        .distinct()
        .all()
    )

def search_combined(base_query, search_term: str, threshold: float):
    """
    Performs Per-Word Fuzzy AND logic.
    Every word in the search query must match either the Item Name OR Category Name.
    """
    print(f"--- Using Per-Word AND Fuzzy search for '{search_term}' ---")
    
    search_words = [word for word in search_term.split() if word]
    if not search_words:
        return []

    # 1. Create the AND filter
    name_conditions = [func.similarity(Item.name_norm, word) > threshold for word in search_words]
    category_conditions = [func.similarity(Item.category_name_norm, word) > threshold for word in search_words]
    
    per_word_fuzzy_match = or_(
        and_(*name_conditions),
        and_(*category_conditions)
    )
    
    # 2. Create the Ranking Score (Average of similarities)
    if len(search_words) > 1:
        avg_name_sim = sum((func.similarity(Item.name_norm, word) for word in search_words), 0.0) / len(search_words)
        avg_cat_sim = sum((func.similarity(Item.category_name_norm, word) for word in search_words), 0.0) / len(search_words)
        per_word_sim_score = func.greatest(avg_name_sim, avg_cat_sim)
    else:
        per_word_sim_score = func.greatest(
            func.similarity(Item.name_norm, search_term),
            func.similarity(Item.category_name_norm, search_term)
        )

    return (
        base_query
        .filter(per_word_fuzzy_match)
        .add_columns(per_word_sim_score)
        .order_by(per_word_sim_score.desc())
        .distinct()
        .all()
    )

def search_semantic(base_query, search_term: str, limit: int = 5):
    """Performs Vector Semantic Search using pgvector."""
    print(f"--- Falling back to semantic search for '{search_term}' ---")
    
    model = get_embedding_model() 
    query_embedding = model.encode(search_term).tolist() 

    distance_col = Item.emb.cosine_distance(query_embedding)
    
    return (
        base_query  
        .add_columns(distance_col)
        .order_by(distance_col.asc()) 
        .distinct()
        .limit(limit)
        .all()
    )

# --- Main List Endpoint ---

@router.get("", response_model=list[ItemOut])
def list_items(
    search: str = Query(None, description="Search query for item name or description."),
    type: str = Query(None, description="Filter by subcategory (e.g., 'veg', 'non-veg')."),
    price_min: float = Query(None, description="Minimum price."),
    price_max: float = Query(None, description="Maximum price."),
    similarity_threshold: float = Query(0.3, description="Similarity threshold for fuzzy search (0 to 1).", ge=0, le=1),
    search_mode: SearchMode = Query(SearchMode.COMBINED, description="Search mode."),
    db: Session = Depends(get_db)
):
    # 1. Build Base Query (Filters)
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

    # 2. Execute Search Strategy
    if search:
        search_term = search.strip()

        if search_mode == SearchMode.FTS_ONLY:
            ordered_id_tuples = search_fts(base_query, search_term)
            
        elif search_mode == SearchMode.FUZZY_ONLY:
            ordered_id_tuples = search_fuzzy(base_query, search_term, similarity_threshold)
            
        elif search_mode == SearchMode.COMBINED:
            ordered_id_tuples = search_combined(base_query, search_term, similarity_threshold)
            
            # Fallback logic specific to COMBINED mode
            if not ordered_id_tuples:
                ordered_id_tuples = search_semantic(base_query, search_term)
    else:
        # No search, just default sort
        ordered_id_tuples = base_query.add_columns(Item.name).order_by(Item.name.asc()).distinct().all()

    # 3. Fetch Full Objects
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

    return [convert_item_to_item_out(item) for item in sorted_items]

@router.get("/test/{item_id}", response_model=ItemOut)
def test_item_loading(item_id: int, db: Session = Depends(get_db)):
    item_obj = db.query(Item).options(
        joinedload(Item.variations), 
        joinedload(Item.category)
    ).filter(Item.id == item_id).first()
    if not item_obj:
        raise HTTPException(404, "Item not found")
    return convert_item_to_item_out(item_obj)

@router.get("/semantic-search", response_model=list[ItemOut])
def semantic_search_items(
    search: str = Query(..., description="A natural language query."),
    limit: int = Query(5, description="Number of results to return."),
    db: Session = Depends(get_db)
):
    model = get_embedding_model() 
    query_embedding = model.encode(search).tolist() 
    items = db.query(Item).options(joinedload(Item.variations), joinedload(Item.category)).order_by(Item.emb.cosine_distance(query_embedding)).limit(limit).all()
    return [convert_item_to_item_out(item) for item in items]

@router.post("", response_model=ItemOut, status_code=201)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    obj = Item(**payload.dict())
    category = db.get(Category, obj.category_id)
    category_name = category.name if category else None
    obj.emb = generate_embedding(payload.dict(), category_name)
    db.add(obj)
    db.commit()
    created_item = db.query(Item).options(joinedload(Item.variations), joinedload(Item.category)).filter(Item.id == obj.id).first()
    return convert_item_to_item_out(created_item)

@router.patch("/{item_id}", response_model=ItemOut)
def update_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db)):
    obj = db.get(Item, item_id)
    if not obj:
        raise HTTPException(404, "Item not found")
    update_data = payload.dict(exclude_unset=True)
    new_category_id = update_data.get("category_id", obj.category_id)
    for key, value in update_data.items():
        setattr(obj, key, value)
    category = db.get(Category, new_category_id)
    category_name = category.name if category else None
    current_data_for_embedding = {"name": obj.name, "description": obj.description, "subcategory": obj.subcategory}
    obj.emb = generate_embedding(current_data_for_embedding, category_name)
    db.commit()
    updated_item = db.query(Item).options(joinedload(Item.variations), joinedload(Item.category)).filter(Item.id == item_id).first()
    return convert_item_to_item_out(updated_item)

@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Item, item_id)
    if not obj:
        raise HTTPException(404, "Item not found")
    db.delete(obj)
    db.commit()