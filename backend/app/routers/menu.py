# backend/app/routers/menu.py
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.session import get_db
# Correctly import Item, PriceVariation, and MenuSpecial
from app.db.models import Item, PriceVariation, MenuSpecial
from app.schemas.menu import (
    MenuSpecialCreate, MenuSpecialUpdate, MenuSpecialOut, PriceVariationOut
)

router = APIRouter(prefix="/menu", tags=["menu"])

# Note: All general item management endpoints were moved to items.py.
# This router is now only for specials and the price resolver.

# --- Specials CRUD ---
@router.get("/specials", response_model=list[MenuSpecialOut])
def list_specials(item_id: int | None = None, db: Session = Depends(get_db)):
    qry = db.query(MenuSpecial)
    if item_id:
        qry = qry.filter(MenuSpecial.item_id == item_id)
    return qry.order_by(MenuSpecial.start_date.desc(), MenuSpecial.id.desc()).all()


@router.post("/specials", response_model=MenuSpecialOut, status_code=201)
def create_special(payload: MenuSpecialCreate, db: Session = Depends(get_db)):
    obj = MenuSpecial(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.patch("/specials/{special_id}", response_model=MenuSpecialOut)
def update_special(special_id: int, payload: MenuSpecialUpdate, db: Session = Depends(get_db)):
    obj = db.get(MenuSpecial, special_id)
    if not obj:
        raise HTTPException(404, "Special not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/specials/{special_id}", status_code=204)
def delete_special(special_id: int, db: Session = Depends(get_db)):
    obj = db.get(MenuSpecial, special_id)
    if not obj:
        raise HTTPException(404, "Special not found")
    db.delete(obj)
    db.commit()


# --- Price resolver ---
@router.get("/resolve-price")
def resolve_price(item_id: int, variation_id: int, at: datetime | None = None, db: Session = Depends(get_db)):
    at = at.astimezone(timezone.utc) if at else datetime.now(timezone.utc)

    # Check for active special
    sp = (
        db.query(MenuSpecial.special_price)
          .filter(
              MenuSpecial.item_id == item_id,
              MenuSpecial.variation_id == variation_id,
              MenuSpecial.is_active.is_(True),
              MenuSpecial.start_date <= at,
              or_(MenuSpecial.end_date.is_(None), MenuSpecial.end_date > at),
          )
          .order_by(MenuSpecial.start_date.desc(), MenuSpecial.id.desc())
          .first()
    )
    if sp and sp[0] is not None:
        return {"price": float(sp[0]), "source": "special_variation"}

    # Fallback to base variation price
    base = db.query(PriceVariation.final_price).filter(PriceVariation.id == variation_id).first()
    if base and base[0] is not None:
        return {"price": float(base[0]), "source": "base_variation"}

    raise HTTPException(404, "No price found")