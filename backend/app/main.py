from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.session import get_db
from app.db.models import MenuItem
from app.schemas.menu import MenuItemOut

router = APIRouter(prefix="/menu", tags=["menu"])

@router.get("", response_model=list[MenuItemOut])
def list_menu(
    q: str | None = Query(None),
    tag: str | None = Query(None),
    db: Session = Depends(get_db)
):
    qry = db.query(MenuItem)
    if q:
        like = f"%{q.lower()}%"
        qry = qry.filter(or_(MenuItem.name.ilike(like), MenuItem.description.ilike(like)))
    if tag:
        qry = qry.filter(MenuItem.tags.ilike(f"%{tag.lower()}%"))
    return qry.order_by(MenuItem.id.asc()).all()

@router.get("/{item_id}", response_model=MenuItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    return db.query(MenuItem).filter(MenuItem.id == item_id).first()
