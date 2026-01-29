from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Float, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base

class OrchestratorValidation(Base):
    __tablename__ = "orchestrator_validations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    stage_number = Column(Integer, nullable=False)

    # Result
    approved = Column(Boolean, nullable=False)
    quality_score = Column(Float, nullable=True) # 0-10
    coherence_score = Column(Float, nullable=True) # 0-10
    
    # Details (JSONB)
    issues = Column(JSONB, default=list) # [{type: 'error', message: '...', field: '...'}]
    suggestions = Column(JSONB, default=list) # [{type: 'suggestion', message: '...'}]
    validation_details = Column(JSONB, nullable=True) # Specific logic checks

    # Metadata
    ai_model_used = Column(String(50), nullable=True)
    validated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    account = relationship("Account")

    # Constraints
    __table_args__ = (
        UniqueConstraint('account_id', 'stage_number', 'validated_at', name='uq_account_stage_validation'),
    )

    def __repr__(self):
        return f"<OrchestratorValidation Stage {self.stage_number} - Approved: {self.approved}>"
