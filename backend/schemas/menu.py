from pydantic import BaseModel

class MenuItemOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    tags: str | None = None
    price_npr: int
    availability: bool
