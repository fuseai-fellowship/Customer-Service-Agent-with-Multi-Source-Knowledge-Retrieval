# backend/app/routers/items.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload # Import 'joinedload'
from app.db.session import get_db
from app.db.models import Item, Category
from app.schemas.menu import ItemOut, ItemCreate, ItemUpdate
from app.core.embedding import generate_embedding

router = APIRouter(prefix="/items", tags=["items"])

@router.get("", response_model=list[ItemOut])
def list_items(db: Session = Depends(get_db)):
    # UPDATED THIS QUERY
    # We now use .options(joinedload(Item.variations)) to fetch all items
    # and their related variations in a single, efficient database query.
    return db.query(Item).options(joinedload(Item.variations)).order_by(Item.name.asc()).all()

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
    # To ensure we get the item and its variations together, we use joinedload here too.
    obj = db.query(Item).options(joinedload(Item.variations)).filter(Item.id == item_id).first()
    if not obj:
        raise HTTPException(404, "Item not found")
        
    update_data = payload.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(obj, key, value)
        
    current_data_for_embedding = {
        "name": obj.name,
        "description": obj.description,
        "subcategory": obj.subcategory
    }
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