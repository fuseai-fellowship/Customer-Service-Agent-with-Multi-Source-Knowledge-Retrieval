# backend/app/schemas/menu.py
from pydantic import BaseModel, ConfigDict, computed_field
from datetime import datetime
from decimal import Decimal

# Category Schemas
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# priceVariation Schemas --
class PriceVariationBase(BaseModel):
    item_id: int
    label: str
    final_price: Decimal
    is_available: bool = True

class PriceVariationCreate(PriceVariationBase):
    pass

class PriceVariationUpdate(BaseModel):
    label: str | None = None
    final_price: Decimal | None = None
    is_available: bool | None = None

class PriceVariationOut(PriceVariationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# Item Schemas 
class ItemBase(BaseModel):
    category_id: int
    subcategory: str | None = None
    name: str
    description: str | None = None
    is_available: bool = True

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    category_id: int | None = None
    subcategory: str | None = None
    name: str | None = None
    description: str | None = None
    is_available: bool | None = None
    emb: list[float] | None = None 

# --- THIS IS THE MODIFIED ItemOut CLASS ---
class ItemOut(ItemBase):
    id: int
    variations: list[PriceVariationOut] = []
    
    # NO @computed_field. Just a regular field.
    category_name: str | None = None 

    model_config = ConfigDict(from_attributes=True)


#MenuSpecial Schema
class MenuSpecialBase(BaseModel):
    item_id: int
    variation_id: int
    variation_label_snapshot: str | None = None
    special_price: Decimal
    start_date: datetime
    end_date: datetime | None = None
    is_active: bool = True

class MenuSpecialCreate(MenuSpecialBase):
    pass

class MenuSpecialUpdate(BaseModel):
    variation_label_snapshot: str | None = None
    special_price: Decimal | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    is_active: bool | None = None

class MenuSpecialOut(MenuSpecialBase):
    id: int
    model_config = ConfigDict(from_attributes=True)