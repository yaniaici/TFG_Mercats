from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Text, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=True)
    preferences = Column(JSONB, default={})
    registration_date = Column(DateTime(timezone=True), server_default=func.now())


class PurchaseHistory(Base):
    __tablename__ = "purchase_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    ticket_id = Column(UUID(as_uuid=True), nullable=False)
    purchase_date = Column(DateTime(timezone=True), nullable=False)
    store_name = Column(String(255), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    products = Column(JSONB, default=[])
    num_products = Column(Integer, default=0)
    ticket_type = Column(String(100), nullable=True)
    is_market_store = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Segment(Base):
    __tablename__ = "segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    # JSON con filtros: { last_days, min_total_spent, min_num_purchases, stores_in, is_market_store, preferences_contains }
    filters = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_segments_name', 'name'),
        Index('idx_segments_is_active', 'is_active'),
    )


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    message = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_campaigns_name', 'name'),
        Index('idx_campaigns_is_active', 'is_active'),
    )


class CampaignSegment(Base):
    __tablename__ = "campaign_segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    segment_id = Column(UUID(as_uuid=True), ForeignKey("segments.id", ondelete="CASCADE"), nullable=False)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True)
    message = Column(Text, nullable=False)
    status = Column(String(20), default="queued")  # queued, sent, failed
    meta = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_notifications_user_id', 'user_id'),
        Index('idx_notifications_campaign_id', 'campaign_id'),
        Index('idx_notifications_status', 'status'),
    )


