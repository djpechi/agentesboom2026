# /backend/app/schemas/stage.py

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Any


class StageUpdate(BaseModel):
    """Schema for updating a stage"""
    status: str | None = Field(None, pattern="^(locked|in_progress|completed)$")
    state: dict[str, Any] | None = None
    output: dict[str, Any] | None = None
    ai_model_used: str | None = None


class StageResponse(BaseModel):
    """Schema for stage response"""
    id: UUID
    account_id: UUID
    stage_number: int
    status: str
    state: dict[str, Any]
    output: dict[str, Any] | None
    ai_model_used: str | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    orchestrator_approved: bool | None = None
    orchestrator_score: float | None = None
    orchestrator_feedback: dict[str, Any] | None = None

    class Config:
        from_attributes = True


class StageMessageRequest(BaseModel):
    """Schema for sending a message to a stage agent"""
    message: str = Field(..., min_length=1)
    state: dict[str, Any] | None = None
