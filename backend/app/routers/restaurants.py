from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Restaurant, OpeningHour
from app.schemas.restaurant import RestaurantOut, OpeningHourOut

router = APIRouter(prefix="/restaurant", tags=["restaurant"])

@router.get("", response_model=RestaurantOut)
def get_restaurant(db: Session = Depends(get_db)):
    r = db.query(Restaurant).first()
    hours = db.query(OpeningHour).filter(OpeningHour.restaurant_id == r.id).order_by(OpeningHour.day_of_week).all()
    return {
        "name": r.name, "slogan": r.slogan, "address": r.address, "phone": r.phone, "about": r.about,
        "hours": [OpeningHourOut(day_of_week=h.day_of_week, open_time=h.open_time, close_time=h.close_time) for h in hours]
    }
