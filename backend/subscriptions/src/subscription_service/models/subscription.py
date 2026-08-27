from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, unique=True, nullable=False)
    
    tier: Mapped[str] = mapped_column(String(50), default="free") # free | premium | pro | family
    status: Mapped[str] = mapped_column(String(50), default="active") # active | past_due | canceled
    
    current_period_start: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    current_period_end: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Provider details (stripe, razorpay, mock)
    provider: Mapped[str] = mapped_column(String(50), default="mock")
    provider_subscription_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Family Plan Link
    family_plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("family_plans.id"), nullable=True)
    family_plan: Mapped[Optional["FamilyPlan"]] = relationship("FamilyPlan", back_populates="members", foreign_keys=[family_plan_id])


class Referral(Base):
    """
    Tracks referral codes and rewarded bonus months ('Give a month, get a month').
    """
    __tablename__ = "referrals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referrer_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    referral_code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    
    referred_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending") # pending | redeemed | rewarded
    reward_days: Mapped[int] = mapped_column(Integer, default=30)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    redeemed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class FamilyPlan(Base):
    """
    Family Plan allowing a primary subscriber to invite up to 4 members under one billing umbrella.
    """
    __tablename__ = "family_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    primary_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    plan_name: Mapped[str] = mapped_column(String(100), default="Family Nutrition Plan")
    max_members: Mapped[int] = mapped_column(Integer, default=5)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    members: Mapped[List["Subscription"]] = relationship("Subscription", back_populates="family_plan", foreign_keys=[Subscription.family_plan_id])
    invites: Mapped[List["FamilyInvite"]] = relationship("FamilyInvite", back_populates="family_plan", cascade="all, delete-orphan")


class FamilyInvite(Base):
    """
    Invites sent to family members by email.
    """
    __tablename__ = "family_invites"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_plans.id"), nullable=False)
    invited_email: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending") # pending | accepted | revoked
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    family_plan: Mapped["FamilyPlan"] = relationship("FamilyPlan", back_populates="invites")
