# /backend/app/routers/stages.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.account import Account
from app.models.stage import Stage
from app.schemas.stage import StageUpdate, StageResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/accounts/{account_id}/stages", tags=["Stages"])


async def verify_account_ownership(
    account_id: UUID,
    current_user: User,
    db: AsyncSession
) -> Account:
    """Helper function to verify account ownership"""
    result = await db.execute(
        select(Account).where(
            Account.id == account_id,
            Account.user_id == current_user.id
        )
    )
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )

    return account


@router.get("", response_model=list[StageResponse])
async def get_stages(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all stages for an account

    Returns stages 1-7 in order
    """
    # Verify ownership
    await verify_account_ownership(account_id, current_user, db)

    # Get all stages
    result = await db.execute(
        select(Stage)
        .where(Stage.account_id == account_id)
        .order_by(Stage.stage_number)
    )
    stages = result.scalars().all()

    return stages


@router.get("/{stage_number}", response_model=StageResponse)
async def get_stage(
    account_id: UUID,
    stage_number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific stage by number (1-7)
    """
    # Verify ownership
    await verify_account_ownership(account_id, current_user, db)

    # Validate stage number
    if stage_number < 1 or stage_number > 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stage number must be between 1 and 7"
        )

    # Get stage
    result = await db.execute(
        select(Stage).where(
            Stage.account_id == account_id,
            Stage.stage_number == stage_number
        )
    )
    stage = result.scalar_one_or_none()

    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )

    return stage


@router.patch("/{stage_number}", response_model=StageResponse)
async def update_stage(
    account_id: UUID,
    stage_number: int,
    stage_data: StageUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a stage

    Used to update status, state, output, etc.
    """
    # Verify ownership
    await verify_account_ownership(account_id, current_user, db)

    # Validate stage number
    if stage_number < 1 or stage_number > 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stage number must be between 1 and 7"
        )

    # Get stage
    result = await db.execute(
        select(Stage).where(
            Stage.account_id == account_id,
            Stage.stage_number == stage_number
        )
    )
    stage = result.scalar_one_or_none()

    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )

    # Update fields
    update_data = stage_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(stage, field, value)

    # If status changed to completed, set completed_at timestamp
    if stage_data.status == "completed" and stage.completed_at is None:
        stage.completed_at = datetime.utcnow()

        # Unlock next stage if it exists
        if stage_number < 7:
            next_stage_result = await db.execute(
                select(Stage).where(
                    Stage.account_id == account_id,
                    Stage.stage_number == stage_number + 1
                )
            )
            next_stage = next_stage_result.scalar_one_or_none()
            if next_stage and next_stage.status == "locked":
                next_stage.status = "in_progress"

    await db.commit()
    await db.refresh(stage)

    return stage


@router.post("/{stage_number}/reset", response_model=StageResponse)
async def reset_stage(
    account_id: UUID,
    stage_number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Reset a stage to its initial state
    
    - Sets status to 'in_progress'
    - Clears state (chat history)
    - Clears output
    - Clears completed_at
    """
    # Verify ownership
    await verify_account_ownership(account_id, current_user, db)

    # Validate stage number
    if stage_number < 1 or stage_number > 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stage number must be between 1 and 7"
        )

    # Get stage
    result = await db.execute(
        select(Stage).where(
            Stage.account_id == account_id,
            Stage.stage_number == stage_number
        )
    )
    stage = result.scalar_one_or_none()

    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    
    # Reset fields
    stage.status = "in_progress"
    stage.state = {} # Clear chat history
    stage.output = None
    stage.completed_at = None
    
    # Also reset ai_model_used if needed? Let's keep it or clear it. Let's clear it.
    stage.ai_model_used = None
    
    # Reset Orchestrator fields
    stage.orchestrator_approved = None
    stage.orchestrator_score = None
    stage.orchestrator_feedback = None

    await db.commit()
    await db.refresh(stage)

    return stage
