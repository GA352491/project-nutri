from sqlalchemy import String, Date, Integer, Float, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import date

from nutriplan_shared.models.base import Base

class MealPlan(Base):
    __tablename__ = "meal_plans"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active") # active, completed, skipped
    
    # Store daily targets as a JSON snapshot for reference
    targets: Mapped[dict] = mapped_column(JSON, nullable=True)

    meals = relationship("MealPlanItem", back_populates="plan", cascade="all, delete-orphan")


class MealPlanItem(Base):
    __tablename__ = "meal_plan_items"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("meal_plans.id"), nullable=False)
    
    date: Mapped[date] = mapped_column(Date, nullable=False)
    meal_type: Mapped[str] = mapped_column(String(20), nullable=False) # breakfast, lunch, dinner, snack
    
    # Reference to the Recipe Service
    recipe_id: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Snapshot of macros for this specific meal for easy querying without joining Recipe service
    calories: Mapped[float] = mapped_column(Float, default=0.0)
    protein_g: Mapped[float] = mapped_column(Float, default=0.0)
    fat_g: Mapped[float] = mapped_column(Float, default=0.0)
    carbs_g: Mapped[float] = mapped_column(Float, default=0.0)
    
    status: Mapped[str] = mapped_column(String(20), default="planned") # planned, logged, skipped

    plan = relationship("MealPlan", back_populates="meals")
