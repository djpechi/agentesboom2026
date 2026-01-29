# /backend/app/routers/accounts.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.account import Account
from app.models.stage import Stage
from app.schemas.account import AccountCreate, AccountUpdate, AccountResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new account (client company)

    Also initializes all 7 stages in 'locked' status
    """
    # Normalize website URL
    website = account_data.company_website
    if website and not website.startswith(('http://', 'https://')):
        website = f'https://{website}'

    # Create new account
    new_account = Account(
        user_id=current_user.id,
        client_name=account_data.client_name,
        company_website=website,
        ai_model=account_data.ai_model
    )

    db.add(new_account)
    await db.flush()  # Get the account ID without committing

    # Create all 7 stages for this account
    for stage_num in range(1, 8):
        stage = Stage(
            account_id=new_account.id,
            stage_number=stage_num,
            status="locked" if stage_num > 1 else "in_progress",  # Stage 1 starts unlocked
            state={}
        )
        db.add(stage)

    await db.commit()
    
    # Reload with stages
    result = await db.execute(
        select(Account)
        .options(selectinload(Account.stages))
        .where(Account.id == new_account.id)
    )
    return result.scalar_one()


@router.get("", response_model=list[AccountResponse])
async def get_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all accounts for the current user
    """
    result = await db.execute(
        select(Account)
        .options(selectinload(Account.stages))
        .where(Account.user_id == current_user.id)
    )
    accounts = result.scalars().all()
    return accounts


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific account by ID

    Must belong to the current user
    """
    result = await db.execute(
        select(Account)
        .options(selectinload(Account.stages))
        .where(
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


@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: UUID,
    account_data: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an account

    Only updates fields that are provided
    """
    # Get account
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

    # Update fields
    update_data = account_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)

    await db.commit()
    await db.refresh(account)

    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an account

    Also deletes all associated stages (CASCADE)
    """
    # Get account
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

    await db.delete(account)
    await db.commit()

    return None
