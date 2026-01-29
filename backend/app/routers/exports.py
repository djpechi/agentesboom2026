# /backend/app/routers/exports.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.account import Account
from app.models.stage import Stage
from app.dependencies import get_current_user
from app.services import pdf_service, excel_service

router = APIRouter(prefix="/exports", tags=["Exports"])


async def get_account_with_stages(
    account_id: UUID,
    current_user: User,
    db: AsyncSession
) -> tuple[Account, dict[int, dict]]:
    """
    Get account and all completed stage outputs

    Returns:
        Tuple of (account, stage_outputs dict)
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

    # Get all completed stages with output
    result = await db.execute(
        select(Stage).where(
            Stage.account_id == account_id,
            Stage.status == "completed",
            Stage.output.isnot(None)
        ).order_by(Stage.stage_number)
    )
    stages = result.scalars().all()

    if not stages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No completed stages to export. Complete at least one stage first."
        )

    # Build stage_outputs dict
    stage_outputs = {
        stage.stage_number: stage.output
        for stage in stages
    }

    return account, stage_outputs


@router.get("/accounts/{account_id}/pdf")
async def export_to_pdf(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export account results to PDF

    Returns a PDF file with all completed stage outputs
    """
    try:
        account, stage_outputs = await get_account_with_stages(
            account_id, current_user, db
        )

        # Generate PDF
        pdf_bytes = pdf_service.generate_pdf(
            account_name=account.client_name,
            company_website=account.company_website,
            stage_outputs=stage_outputs,
            consultant_name=current_user.full_name or "BOOMS AI"
        )

        # Return as downloadable PDF
        filename = f"{account.client_name.replace(' ', '_')}_report.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating PDF: {str(e)}"
        )


@router.get("/accounts/{account_id}/excel")
async def export_to_excel(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export account results to Excel

    Returns an Excel file with all completed stage outputs
    """
    try:
        account, stage_outputs = await get_account_with_stages(
            account_id, current_user, db
        )

        # Generate Excel
        excel_bytes = excel_service.generate_excel(
            account_name=account.client_name,
            company_website=account.company_website,
            stage_outputs=stage_outputs
        )

        # Return as downloadable Excel
        filename = f"{account.client_name.replace(' ', '_')}_report.xlsx"

        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating Excel: {str(e)}"
        )
