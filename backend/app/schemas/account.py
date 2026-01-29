# /backend/app/schemas/account.py

from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from uuid import UUID


class AccountCreate(BaseModel):
    """Schema for creating a new account"""
    client_name: str = Field(..., min_length=1, max_length=255)
    company_website: str | None = None
    ai_model: str = "gpt-4o"


class AccountUpdate(BaseModel):
    """Schema for updating an account"""
    client_name: str | None = Field(None, min_length=1, max_length=255)
    company_website: str | None = None
    ai_model: str | None = None


class AccountResponse(BaseModel):
    """Schema for account response"""
    id: UUID
    user_id: UUID
    client_name: str
    company_website: str | None
    ai_model: str
    created_at: datetime
    updated_at: datetime
    stages: list["StageResponse"] = []

    class Config:
        from_attributes = True

from .stage import StageResponse
AccountResponse.model_rebuild()
