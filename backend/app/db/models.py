# backend/app/db/models.py
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
import uuid

from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
from sqlalchemy import (
    String, Boolean, Integer, ForeignKey, Text, DateTime, Numeric, UniqueConstraint
)
# Import new types for FTS
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

Base = declarative_base()

# --- User, Restaurant, OpeningHour, Category models remain the same ---
class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class Restaurant(Base):
    __tablename__ = "restaurant"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text)
    slogan: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(Text, nullable=True)
    about: Mapped[str | None] = mapped_column(Text, nullable=True)
    opening_hours: Mapped[list[OpeningHour]] = relationship("OpeningHour", back_populates="restaurant", cascade="all, delete-orphan")
    categories: Mapped[list["Category"]] = relationship("Category", back_populates="restaurant", cascade="all, delete-orphan")

class OpeningHour(Base):
    __tablename__ = "opening_hours"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("restaurant.id"))
    day_of_week: Mapped[int] = mapped_column(Integer)
    open_time: Mapped[str] = mapped_column(String)
    close_time: Mapped[str] = mapped_column(String)
    restaurant: Mapped[Restaurant] = relationship("Restaurant", back_populates="opening_hours")

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("restaurant.id"), default=uuid.UUID('00000000-0000-0000-0000-000000000001'))
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    restaurant: Mapped[Restaurant] = relationship("Restaurant", back_populates="categories")
    items: Mapped[list["Item"]] = relationship("Item", back_populates="category", cascade="all, delete-orphan")

# --- UPDATED Item MODEL ---
class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), index=True)
    subcategory: Mapped[str | None] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    # --- Search-related columns ---
    name_norm: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_norm: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_name_norm: Mapped[str | None] = mapped_column(Text, nullable=True)
    tsv: Mapped[TSVECTOR | None] = mapped_column(TSVECTOR, nullable=True)
    
    # CORRECTED THE VECTOR SIZE FROM 1536 to 384
    emb: Mapped[list[float] | None] = mapped_column(Vector(384), nullable=True)

    # Relationships
    category: Mapped[Category] = relationship("Category", back_populates="items")
    variations: Mapped[list["PriceVariation"]] = relationship("PriceVariation", back_populates="item", cascade="all, delete-orphan")
    specials: Mapped[list["MenuSpecial"]] = relationship("MenuSpecial", back_populates="item", cascade="all, delete-orphan")


# --- PriceVariation and MenuSpecial models remain the same ---
class PriceVariation(Base):
    __tablename__ = "price_variations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String, nullable=False)
    final_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    item: Mapped[Item] = relationship("Item", back_populates="variations")
    specials: Mapped[list["MenuSpecial"]] = relationship("MenuSpecial", back_populates="variation")
    __table_args__ = (UniqueConstraint("item_id", "label", name="uq_price_variation_item_label"),)

class MenuSpecial(Base):
    __tablename__ = "menu_specials"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"), index=True)
    variation_id: Mapped[int] = mapped_column(ForeignKey("price_variations.id", ondelete="CASCADE"), index=True)
    variation_label_snapshot: Mapped[str | None] = mapped_column(String, nullable=True)
    special_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    item: Mapped[Item] = relationship("Item", back_populates="specials")
    variation: Mapped[PriceVariation] = relationship("PriceVariation", back_populates="specials")
    
class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # This matches the 'emb' column in your 'Item' model
    emb: Mapped[list[float] | None] = mapped_column(Vector(384), nullable=True)