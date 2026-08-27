from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy declarative models."""
    pass

class TimestampMixin:
    """Mixin to add created_at and updated_at columns."""
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now())
