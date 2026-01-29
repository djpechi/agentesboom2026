# /backend/app/models/account.py

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    client_name = Column(String(255), nullable=False)
    company_website = Column(String(500), nullable=True)
    ai_model = Column(String(50), nullable=False, default="gpt-4o")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="accounts")
    stages = relationship("Stage", back_populates="account", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Account {self.client_name}>"
