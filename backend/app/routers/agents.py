# /backend/app/routers/agents.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.account import Account
from app.models.stage import Stage
from app.schemas.stage import StageMessageRequest
from app.dependencies import get_current_user
from app.agents import booms_agent, journey_agent, ofertas_agent, canales_agent, atlas_agent, planner_agent, budgets_agent
from app.services import research_service
from app.services.orchestrator_service import OrchestratorService
from app.models.orchestrator_validation import OrchestratorValidation as OrchestratorValidationModel

router = APIRouter(prefix="/agents", tags=["AI Agents"])


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


@router.post("/accounts/{account_id}/stages/{stage_number}/chat")
async def chat_with_agent(
    account_id: UUID,
    stage_number: int,
    request: StageMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to an agent for a specific stage

    The agent processes the message and updates the stage state
    """
    # Verify ownership
    account = await verify_account_ownership(account_id, current_user, db)

    # Validate stage number
    if stage_number < 1 or stage_number > 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stage number must be between 1 and 7"
        )

    # Only stages 1-7 are implemented
    if stage_number > 7:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Stage {stage_number} not yet implemented in MVP"
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

    # Check if stage is locked
    if stage.status == "locked":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This stage is locked. Complete previous stages first."
        )

    # Check if stage is already completed
    if stage.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This stage is already completed. Cannot send more messages."
        )

    # Get previous stage output if needed (for stage 2)
    previous_stage_output = None
    if stage_number > 1:
        prev_result = await db.execute(
            select(Stage).where(
                Stage.account_id == account_id,
                Stage.stage_number == stage_number - 1
            )
        )
        prev_stage = prev_result.scalar_one_or_none()
        if prev_stage and prev_stage.output:
            previous_stage_output = prev_stage.output

    # Get outputs from all previous stages for context (especially for Stage 3-7)
    previous_outputs = {}
    if stage_number > 1:
        # Fetch all previous stages
        prev_stages_result = await db.execute(
            select(Stage).where(
                Stage.account_id == account_id,
                Stage.stage_number < stage_number
            )
        )
        for p_stage in prev_stages_result.scalars().all():
            previous_outputs[f"stage_{p_stage.stage_number}"] = p_stage.output

    # Route to appropriate agent
    try:
        # Prepare account context for agents
        account_context = {
            "company_name": account.client_name,
            "company_website": account.company_website,
            "consultant_name": current_user.full_name or "Consultor"
        }

        if stage_number == 1:
            # BOOMS agent
            research_found = stage.state.get("research_data")
            agent_response = await booms_agent.process_message(
                message=request.message,
                state=request.state or stage.state,
                account_context=account_context,
                research_context=research_found,
                ai_model=account.ai_model
            )
        elif stage_number == 2:
            # Journey agent
            agent_response = await journey_agent.process_message(
                message=request.message,
                state=request.state or stage.state,
                previous_stage_output=previous_stage_output,
                ai_model=account.ai_model
            )
        elif stage_number == 3:
            # Ofertas agent (Agent 3) - Uses RAG and outputs from 1 & 2
            agent_response = await ofertas_agent.process_message(
                message=request.message,
                state=request.state or stage.state,
                previous_stage_outputs=previous_outputs,
                ai_model=account.ai_model
            )
        elif stage_number == 4:
            # Canales agent (Agent 4) - Uses Perplexity (simulated)
            agent_response = await canales_agent.process_message(
                message=request.message,
                state=request.state or stage.state,
                previous_stage_outputs=previous_outputs,
                ai_model=account.ai_model
            )
        elif stage_number == 5:
            # Atlas agent (Agent 5) - SEO/AEO Strategist
            agent_response = await atlas_agent.process_message(
                message=request.message,
                state=request.state or stage.state,
                previous_stage_outputs=previous_outputs,
                ai_model=account.ai_model
            )
        elif stage_number == 6:
            # Planner agent (Agent 6) - Content Scheduler
            agent_response = await planner_agent.process_message(
                message=request.message,
                state=request.state or stage.state,
                previous_stage_outputs=previous_outputs,
                ai_model=account.ai_model
            )
        elif stage_number == 7:
            # Budgets agent (Agent 7) - Media Planner
            agent_response = await budgets_agent.process_message(
                message=request.message,
                state=request.state or stage.state,
                previous_stage_outputs=previous_outputs,
                ai_model=account.ai_model
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Agent for stage {stage_number} not implemented"
            )

        # Update stage state
        stage.state = agent_response["state"]
        stage.ai_model_used = account.ai_model

        stage.ai_model_used = account.ai_model

        # If agent completed, update stage and VALIDATE with ORCHESTRATOR
        orchestrator_validation_result = None
        
        if agent_response["completed"]:
            # 1. Orchestrator Validation
            try:
                orchestrator = OrchestratorService()
                
                validation = await orchestrator.validate_stage_completion(
                    account_id=str(account_id),
                    stage_number=stage_number,
                    stage_output=agent_response["output"],
                    previous_outputs=previous_outputs,
                    account_context=account_context
                )
                orchestrator_validation_result = validation.dict()

                # 2. Save Validation to DB
                db_validation = OrchestratorValidationModel(
                    account_id=account_id,
                    stage_number=stage_number,
                    approved=validation.approved,
                    quality_score=validation.qualityScore,
                    coherence_score=validation.coherenceScore,
                    issues=[i.dict() for i in validation.issues],
                    suggestions=[s.dict() for s in validation.suggestions],
                    validation_details=validation.validationDetails,
                    ai_model_used=validation.metadata.get("modelUsed")
                )
                db.add(db_validation)
                
                # 3. Update Stage with Orchestrator Feedback
                stage.orchestrator_approved = validation.approved
                stage.orchestrator_score = validation.overallScore
                stage.orchestrator_feedback = {
                    "issues": [i.dict() for i in validation.issues],
                    "suggestions": [s.dict() for s in validation.suggestions]
                }

                # 4. Decide on Status
                if validation.canProceed:
                     stage.status = "completed"
                     stage.output = agent_response["output"]
                     stage.completed_at = datetime.utcnow()
                     
                     # Unlock next stage
                     if stage_number < 7:
                        next_result = await db.execute(
                            select(Stage).where(
                                Stage.account_id == account_id,
                                Stage.stage_number == stage_number + 1
                            )
                        )
                        next_stage = next_result.scalar_one_or_none()
                        if next_stage and next_stage.status == "locked":
                            next_stage.status = "in_progress"
                else:
                    # Logic: If rejected, we keep it 'in_progress' so user can continue chatting
                    # We might want to append a message from the Orchestrator?
                    # For now, just keeping status as is (which is 'in_progress' usually)
                    stage.status = "in_progress" 
                    # We DO NOT save output if rejected, or maybe we do? 
                    # Let's save output so user can see it, but status is not completed.
                    # Actually, if we save output, frontend might show it as final?
                    # Let's invalid output => output = None or partial?
                    # Safe bet: Update output so we see the latest draft, but status is NOT completed.
                    stage.output = agent_response["output"]

            except Exception as e:
                print(f"Orchestrator Failed: {e}")
                # Fallback: Mark as completed if orchestrator fails? Or Block?
                # MVP: Fail open (allow completion) but log error
                stage.status = "completed" 
                stage.output = agent_response["output"]
                stage.completed_at = datetime.utcnow()
                stage.orchestrator_approved = True # Default to true on error
                
                if stage_number < 7:
                    next_result = await db.execute(
                        select(Stage).where(
                            Stage.account_id == account_id,
                            Stage.stage_number == stage_number + 1
                        )
                    )
                    next_stage = next_result.scalar_one_or_none()
                    if next_stage and next_stage.status == "locked":
                        next_stage.status = "in_progress"

        await db.commit()
        await db.refresh(stage)

        return {
            "response": agent_response["response"],
            "completed": agent_response["completed"],
            "buttons": agent_response.get("buttons", []),
            "confidenceScore": agent_response.get("confidenceScore"),
            "progressLabel": agent_response.get("progressLabel"),
            "progressStep": agent_response.get("progressStep"),
            "orchestratorValidation": orchestrator_validation_result,
            "stage": {
                "id": stage.id,
                "stage_number": stage.stage_number,
                "status": stage.status,
                "state": stage.state,
                "output": stage.output,
                "completed_at": stage.completed_at,
                "orchestrator_approved": stage.orchestrator_approved,
                "orchestrator_score": stage.orchestrator_score,
                "orchestrator_feedback": stage.orchestrator_feedback
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent error: {str(e)}"
        )


@router.get("/accounts/{account_id}/stages/{stage_number}/init")
async def get_agent_initial_message(
    account_id: UUID,
    stage_number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    print(f"DEBUG: Initializing agent message for stage {stage_number}, account {account_id}")
    # Verify ownership
    account = await verify_account_ownership(account_id, current_user, db)

    # Validate stage number
    if stage_number < 1 or stage_number > 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stage number must be between 1 and 7"
        )

    # Only stages 1-7 are implemented in MVP
    if stage_number > 7:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Stage {stage_number} not yet implemented in MVP"
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

    # Check if stage is locked
    if stage.status == "locked":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This stage is locked. Complete previous stages first."
        )

    # Get previous stage output if needed
    previous_stage_output = None
    if stage_number > 1:
        prev_result = await db.execute(
            select(Stage).where(
                Stage.account_id == account_id,
                Stage.stage_number == stage_number - 1
            )
        )
        prev_stage = prev_result.scalar_one_or_none()
        if prev_stage and prev_stage.output:
            previous_stage_output = prev_stage.output

    # Get all previous outputs for Stage 3 context
    previous_outputs = {}
    if stage_number > 1:
        prev_stages_result = await db.execute(
            select(Stage).where(
                Stage.account_id == account_id,
                Stage.stage_number < stage_number
            )
        )
        for p_stage in prev_stages_result.scalars().all():
            previous_outputs[f"stage_{p_stage.stage_number}"] = p_stage.output

    # Prepare account context
    account_context = {
        "company_name": account.client_name,
        "company_website": account.company_website,
        "consultant_name": current_user.full_name or "Consultor"
    }

    # Get initial message from appropriate agent
    try:
        print(f"DEBUG: Starting initial message logic for stage {stage_number}")
        if stage_number == 1:
            # Ensure state is a dict
            if stage.state is None:
                stage.state = {}
                
            # Check if research already exists
            research_data = stage.state.get("research_data")
            if not research_data and account.company_website:
                print(f"DEBUG: Triggering research for {account.client_name}")
                try:
                    # Perform one-time research
                    research_data = await research_service.research_company(account.client_name, account.company_website)
                    stage.state["research_data"] = research_data
                    await db.commit()
                    print(f"DEBUG: Research completed: {bool(research_data)}")
                except Exception as e:
                    print(f"ERROR: Research failed: {str(e)}")
                    research_data = {}
            
            initial_data = await booms_agent.get_initial_message(account_context, research_context=research_data)
            initial_message = initial_data["message"]
            buttons = initial_data.get("buttons", [])
        elif stage_number == 2:
            # Enrich context for Journey Agent
            context_payload = (previous_stage_output or {}).copy()
            context_payload['brand_name'] = account.client_name
            
            # Try to get industry from Stage 1 research state if available
            if stage_number == 2: # Redundant check but clear intent
                 # We need to fetch Stage 1 state specifically if we want industry
                 # optimized: previous_stage (prev_result) usually has state if we didn't filter columns
                 # But we scalar_one_or_none()'d it.
                 pass 

            initial_message = await journey_agent.get_initial_message(context_payload)
            buttons = []
        else:
            # ... other agents
            buttons = []
            if stage_number == 3: initial_message = await ofertas_agent.get_initial_message(previous_outputs)
            elif stage_number == 4: initial_message = await canales_agent.get_initial_message(previous_outputs)
            elif stage_number == 5: initial_message = await atlas_agent.get_initial_message(previous_outputs)
            elif stage_number == 6: initial_message = await planner_agent.get_initial_message(previous_outputs)
            elif stage_number == 7: initial_message = await budgets_agent.get_initial_message(previous_outputs)
            else:
                 raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail=f"Agent for stage {stage_number} not implemented"
                )

        print(f"DEBUG: Returning initial message successfully")
        return {
            "message": initial_message,
            "buttons": buttons,
            "stage_number": stage_number,
            "status": stage.status
        }

    except Exception as e:
        print(f"CRITICAL ERROR in get_agent_initial_message: {str(e)}")
        # Return a fallback message instead of crashing
        return {
            "message": f"Hola {account_context.get('consultant_name')}, bienvenido a BOOMS Platform. Estamos listos para comenzar con {account.client_name}, aunque hubo un pequeño problema técnico al cargar el contexto inicial. ¿Empezamos con algunas preguntas básicas?",
            "buttons": ["Comenzar", "Reintentar investigación"],
            "stage_number": stage_number,
            "status": stage.status
        }

