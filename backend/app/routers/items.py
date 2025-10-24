# backend/app/routers/items.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from app.db.session import get_db
from app.db.models import Item, Category, PriceVariation
from app.schemas.menu import ItemOut, ItemCreate, ItemUpdate
from app.core.embedding import generate_embedding, get_embedding_model
from pgvector.sqlalchemy import Vector
from enum import Enum # Import Enum

# Define Enum for clear search mode options
class SearchMode(str, Enum):
    COMBINED = "combined"
    FTS_ONLY = "fts_only"
    FUZZY_ONLY = "fuzzy_only"

router = APIRouter(prefix="/items", tags=["items"])

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
    """
    query = db.query(Item).options(joinedload(Item.variations)) # Eager load variations

    # --- Type and Price Filters ---
    if type:
        query = query.filter(func.lower(Item.subcategory) == type.lower())

    if price_min is not None or price_max is not None:
        query = query.join(Item.variations)
        if price_min is not None:
            query = query.filter(PriceVariation.final_price >= price_min)
        if price_max is not None:
            query = query.filter(PriceVariation.final_price <= price_max)

    # --- Conditional Search Logic ---
    if search:
        search_term = search.strip()
        
        # --- Define scores for FTS and Fuzzy ---
        ts_query = func.plainto_tsquery('simple', search_term)
        fts_match = Item.tsv.op('@@')(ts_query)
        fts_rank = func.ts_rank(Item.tsv, ts_query).label('rank')
        
        fuzzy_match = func.similarity(Item.name_norm, search_term) > similarity_threshold
        sim_score = func.similarity(Item.name_norm, search_term).label('sim')

        # Apply the filter based on the selected mode
        if search_mode == SearchMode.COMBINED:
            
            # 1. Create a hybrid score. You can adjust the "weights" (e.g., 1.0 vs 0.5)
            #    to prioritize one score over the other.
            hybrid_score = (fts_rank * 1.0) + (sim_score * 0.5)
            
            # 2. Filter: Use or_ to get all possible matches (like you do now)
            query = query.filter(or_(fts_match, fuzzy_match))
            
            # 3. Add columns so we can order by them
            query = query.add_columns(hybrid_score.label('relevance'), fts_rank, sim_score)
            
            # 4. Order by the new hybrid score. This is your "balance".
            query = query.order_by(hybrid_score.desc())

        elif search_mode == SearchMode.FTS_ONLY:
            query = query.filter(fts_match)
            query = query.add_columns(fts_rank).order_by(fts_rank.desc())

        elif search_mode == SearchMode.FUZZY_ONLY:
            query = query.filter(fuzzy_match)
            query = query.add_columns(sim_score).order_by(sim_score.desc())

        # ... (rest of the function for processing results is the same) ...
        query_results = query.all()

        unique_items = {}
        for row in query_results:
            item_obj = row[0] 
            
            if item_obj.id not in unique_items:
                unique_items[item_obj.id] = item_obj
        results = list(unique_items.values())

    else:
        results = query.distinct().order_by(Item.name.asc()).all()

    return results

# --- Semantic Search Endpoint (Unchanged) ---
@router.get("/semantic-search", response_model=list[ItemOut])
def semantic_search_items(
    search: str = Query(..., description="A natural language query."),
    limit: int = Query(5, description="Number of results to return."),
    db: Session = Depends(get_db)
):
    model = get_embedding_model() 
    query_embedding = model.encode(search).tolist() 

    results = db.query(Item).options(joinedload(Item.variations)).order_by(Item.emb.l2_distance(query_embedding)).limit(limit).all()
    return results

# --- POST, PATCH, DELETE Endpoints (Unchanged) ---
@router.post("", response_model=ItemOut, status_code=201)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    obj = Item(**payload.dict())
    category = db.get(Category, obj.category_id)
    category_name = category.name if category else None
    obj.emb = generate_embedding(payload.dict(), category_name) # Generate embedding on create
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.patch("/{item_id}", response_model=ItemOut)
def update_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db)):
    obj = db.query(Item).options(joinedload(Item.variations)).filter(Item.id == item_id).first()
    if not obj:
        raise HTTPException(404, "Item not found")
    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(obj, key, value)
    current_data_for_embedding = {"name": obj.name, "description": obj.description, "subcategory": obj.subcategory}
    category = db.get(Category, obj.category_id)
    category_name = category.name if category else None
    obj.emb = generate_embedding(current_data_for_embedding, category_name) # Regenerate embedding on update
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Item, item_id)
    if not obj:
        raise HTTPException(404, "Item not found")
    db.delete(obj)
    db.commit()