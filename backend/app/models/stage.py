# /backend/app/models/stage.py

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Stage(Base):
    __tablename__ = "stages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    stage_number = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default="locked")  # locked, in_progress, completed
    state = Column(JSONB, default=dict, nullable=False)  # Estado actual de la conversación
    output = Column(JSONB, nullable=True)  # Output final cuando se completa
    ai_model_used = Column(String(50), nullable=True)
    
    # Orchestrator Fields
    orchestrator_approved = Column(Boolean, nullable=True) # None = not validated, True/False
    orchestrator_score = Column(Float, nullable=True)
    orchestrator_feedback = Column(JSONB, nullable=True) # { issues: [], suggestions: [] }

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    account = relationship("Account", back_populates="stages")

    # Constraints
    __table_args__ = (
        UniqueConstraint('account_id', 'stage_number', name='uq_account_stage'),
        CheckConstraint('stage_number >= 1 AND stage_number <= 7', name='ck_stage_number'),
        CheckConstraint("status IN ('locked', 'in_progress', 'completed')", name='ck_status'),
    )

    def __repr__(self):
        return f"<Stage {self.stage_number} - {self.status}>"
