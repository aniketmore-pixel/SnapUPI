from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from backend_db import Base

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    tx_id = Column(String(64), unique=True, nullable=False, index=True)
    from_upi = Column(String(128), nullable=True)
    to_upi = Column(String(128), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(32), nullable=False, default="PENDING")  # PENDING / SUCCESS / FAILED
    attempt_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
