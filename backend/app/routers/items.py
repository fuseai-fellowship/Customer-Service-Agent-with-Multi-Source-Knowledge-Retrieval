# backend/app/routers/items.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_ # Import 'or_'
from app.db.session import get_db
from app.db.models import Item, Category, PriceVariation
from app.schemas.menu import ItemOut, ItemCreate, ItemUpdate
from app.core.embedding import generate_embedding
from pgvector.sqlalchemy import Vector

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[ItemOut])
def list_items(
    search: str = Query(None, description="Search query for item name or description."),
    type: str = Query(None, description="Filter by subcategory (e.g., 'veg', 'non-veg')."),
    price_min: float = Query(None, description="Minimum price."),
    price_max: float = Query(None, description="Maximum price."),
    similarity_threshold: float = Query(0.3, description="Similarity threshold for fuzzy search (0 to 1). Higher means stricter matching.", ge=0, le=1), # Added threshold parameter
    db: Session = Depends(get_db)
):
    """
    Get menu items with filtering, ranked FTS, and fuzzy search for typos.
    """
    query = db.query(Item).options(joinedload(Item.variations))

    # --- Type and Price Filters (Unchanged) ---
    if type:
        query = query.filter(func.lower(Item.subcategory) == type.lower())

    if price_min is not None or price_max is not None:
        query = query.join(Item.variations)
        if price_min is not None:
            query = query.filter(PriceVariation.final_price >= price_min)
        if price_max is not None:
            query = query.filter(PriceVariation.final_price <= price_max)

    # --- Combined FTS and Fuzzy Search Logic ---
    if search:
        search_term = search.strip()
        
        # 1. Prepare Full-Text Search query
        ts_query = func.plainto_tsquery('simple', search_term)
        rank = func.ts_rank(Item.tsv, ts_query).label('rank') # For ranking results
        fts_match = Item.tsv.op('@@')(ts_query) # The FTS match condition

        # 2. Prepare Fuzzy Search (pg_trgm) condition
        # This checks if the normalized name is similar enough to the search term
        fuzzy_match = func.similarity(Item.name_norm, search_term) > similarity_threshold

        # 3. Combine conditions: Find items that EITHER match FTS OR are similar enough (fuzzy)
        query = query.filter(or_(fts_match, fuzzy_match))

        # 4. Add ranking (based on FTS) and order by it (best FTS matches first)
        query = query.add_columns(rank).order_by(rank.desc())

        # 5. Execute and process results
        ranked_results = query.all() # Fetch all potential matches (including duplicates if price filter was used)
        
        # Use a dictionary to keep only unique items, prioritizing the first encounter (highest rank)
        unique_items = {}
        for item, rank_val in ranked_results:
             if item.id not in unique_items:
                 unique_items[item.id] = item
        results = list(unique_items.values())

    else:
        # If no search term, just apply distinct and order by name
        results = query.distinct().order_by(Item.name.asc()).all()

    return results

# --- Semantic Search Endpoint (Unchanged) ---
@router.get("/semantic-search", response_model=list[ItemOut])
def semantic_search_items(
    search: str = Query(..., description="A natural language query (e.g., 'something spicy and warm')."),
    limit: int = Query(5, description="Number of results to return."),
    db: Session = Depends(get_db)
):
    query_embedding = generate_embedding({"name": search}, None)
    results = db.query(Item).options(joinedload(Item.variations)).order_by(Item.emb.l2_distance(query_embedding)).limit(limit).all()
    return results

# --- POST, PATCH, DELETE Endpoints (Unchanged) ---
@router.post("", response_model=ItemOut, status_code=201)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    obj = Item(**payload.dict())
    category = db.get(Category, obj.category_id)
    category_name = category.name if category else None
    obj.emb = generate_embedding(payload.dict(), category_name)
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
    obj.emb = generate_embedding(current_data_for_embedding, category_name)
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