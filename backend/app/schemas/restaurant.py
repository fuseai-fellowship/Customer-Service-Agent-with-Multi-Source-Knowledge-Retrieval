from pydantic import BaseModel

class OpeningHourOut(BaseModel):
    day_of_week: int
    open_time: str
    close_time: str

class RestaurantOut(BaseModel):
    name: str
    slogan: str | None = None
    address: str | None = None
    phone: str | None = None
    about: str | None = None
    hours: list[OpeningHourOut]
