# /backend/app/routers/demo.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from uuid import UUID

from app.database import get_db
from app.dependencies import get_current_user
from app.services.demo_service import DemoService
from app.models.user import User

router = APIRouter(prefix="/demo", tags=["Demo/Testing"])
demo_service = DemoService()

class DemoRequest(BaseModel):
    profile: str = "saas_b2b"
    speed: str = "normal"

from fastapi.responses import StreamingResponse

@router.post("/accounts/{account_id}/stages/{stage_number}/run")
async def run_stage_demo(
    account_id: UUID,
    stage_number: int,
    request: DemoRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Run an automated demo chat for a specific stage
    """
    # Verify account ownership (simple check)
    from app.routers.agents import verify_account_ownership
    await verify_account_ownership(account_id, current_user, db)
    
    try:
        # Create generator
        stream_generator = demo_service.run_demo_autochat_stream(
            account_id=str(account_id),
            stage_number=stage_number,
            profile_key=request.profile,
            speed=request.speed,
            db=db
        )
        
        return StreamingResponse(
            stream_generator, 
            media_type="text/event-stream"
        )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
