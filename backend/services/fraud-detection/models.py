from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from shared.utils.database import Base

class TransactionAnalysis(Base):
    __tablename__ = 'transaction_analysis'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    transaction_hash = Column(String(66), nullable=True)
    chain_id = Column(Integer, nullable=False)
    from_address = Column(String(42), nullable=False)
    to_address = Column(String(42), nullable=True)
    value = Column(String(100), nullable=True)
    risk_score = Column(Float, nullable=False)
    simulation_result = Column(JSON, nullable=True)
    threats_detected = Column(JSON, nullable=True)
    status = Column(String(20), default='analyzed')
    analyzed_at = Column(DateTime, default=datetime.utcnow)

class MaliciousContract(Base):
    __tablename__ = 'malicious_contracts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_address = Column(String(42), nullable=False, index=True)
    chain_id = Column(Integer, nullable=False)
    threat_type = Column(String(50), nullable=False)
    risk_score = Column(Float, nullable=False)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    evidence = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)

class TokenApproval(Base):
    __tablename__ = 'token_approvals'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    chain_id = Column(Integer, nullable=False)
    token_address = Column(String(42), nullable=False)
    spender_address = Column(String(42), nullable=False)
    amount = Column(String(100), nullable=True)
    is_unlimited = Column(Boolean, default=False)
    approved_at = Column(DateTime, default=datetime.utcnow)
    last_checked = Column(DateTime, default=datetime.utcnow)
