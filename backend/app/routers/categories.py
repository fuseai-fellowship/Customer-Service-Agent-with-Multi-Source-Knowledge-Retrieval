# backend/app/routers/categories.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Category
from app.schemas.menu import CategoryOut, CategoryCreate, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.name.asc()).all()

@router.post("", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    obj = Category(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.patch("/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)):
    obj = db.get(Category, category_id)
    if not obj:
        raise HTTPException(404, "Category not found")
    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    obj = db.get(Category, category_id)
    if not obj:
        raise HTTPException(404, "Category not found")
    db.delete(obj)
    db.commit()