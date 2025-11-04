from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from shared.utils.database import Base

class Subscription(Base):
    __tablename__ = 'subscriptions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    plan_type = Column(String(50), nullable=False)  # free, basic, premium, enterprise
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)  # USD, NGN
    status = Column(String(20), default='active')  # active, expired, cancelled
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    auto_renew = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    subscription_id = Column(UUID(as_uuid=True), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)
    payment_method = Column(String(50), nullable=False)  # usdt, paystack
    transaction_hash = Column(String(66), nullable=True)  # For USDT payments
    paystack_reference = Column(String(100), nullable=True)  # For Paystack
    chain_id = Column(Integer, nullable=True)  # For USDT payments
    status = Column(String(20), default='pending')  # pending, completed, failed
    community_id = Column(UUID(as_uuid=True), nullable=True)
    commission_amount = Column(Float, default=0.0)
    metadata = Column(JSON, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class CommissionEarning(Base):
    __tablename__ = 'commission_earnings'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    community_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # Community leader
    amount = Column(Float, nullable=False)
    status = Column(String(20), default='pending')  # pending, paid, cancelled
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    paid_at = Column(DateTime, nullable=True)
    payment_reference = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
