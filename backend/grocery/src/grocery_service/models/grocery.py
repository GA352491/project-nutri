from sqlalchemy import String, Boolean, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass


class GroceryList(Base):
    __tablename__ = "grocery_lists"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), default="Weekly List")

    items = relationship("GroceryItem", back_populates="list", cascade="all, delete-orphan")


class GroceryItem(Base):
    __tablename__ = "grocery_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    list_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("grocery_lists.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[str] = mapped_column(String(100), default="1")
    unit: Mapped[str] = mapped_column(String(50), default="")
    category: Mapped[str] = mapped_column(String(100), default="General")
    is_checked: Mapped[bool] = mapped_column(Boolean, default=False)

    # Optional link to a recipe that generated this item
    source_recipe_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    list = relationship("GroceryList", back_populates="items")
