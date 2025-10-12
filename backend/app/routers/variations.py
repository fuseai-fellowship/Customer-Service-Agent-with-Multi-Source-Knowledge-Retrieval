# backend/app/routers/variations.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import PriceVariation
from app.schemas.menu import PriceVariationOut, PriceVariationCreate, PriceVariationUpdate

router = APIRouter(prefix="/variations", tags=["variations"])

@router.get("", response_model=list[PriceVariationOut])
def list_variations(item_id: int | None = None, db: Session = Depends(get_db)):
    qry = db.query(PriceVariation)
    if item_id:
        qry = qry.filter(PriceVariation.item_id == item_id)
    return qry.order_by(PriceVariation.id.asc()).all()

@router.post("", response_model=PriceVariationOut, status_code=201)
def create_variation(payload: PriceVariationCreate, db: Session = Depends(get_db)):
    obj = PriceVariation(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.patch("/{variation_id}", response_model=PriceVariationOut)
def update_variation(variation_id: int, payload: PriceVariationUpdate, db: Session = Depends(get_db)):
    obj = db.get(PriceVariation, variation_id)
    if not obj:
        raise HTTPException(404, "Price variation not found")
    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{variation_id}", status_code=204)
def delete_variation(variation_id: int, db: Session = Depends(get_db)):
    obj = db.get(PriceVariation, variation_id)
    if not obj:
        raise HTTPException(404, "Price variation not found")
    db.delete(obj)
    db.commit()