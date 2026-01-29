# /backend/app/services/demo_service.py

import asyncio
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services import ai_provider_service
from app.services.demo_profiles import DEMO_PROFILES
from app.models.stage import Stage
from app.models.account import Account
from app.agents import booms_agent, journey_agent, ofertas_agent, canales_agent, atlas_agent, planner_agent, budgets_agent

class DemoService:
    async def run_demo_autochat_stream(
        self,
        account_id: str,
        stage_number: int,
        profile_key: str = "saas_b2b",
        speed: str = "normal",
        db: AsyncSession = None
    ):
        """
        Executes a full autochat for a specific stage, yielding events as they happen
        """
        import json
        
        # Get stage
        result = await db.execute(
            select(Stage).where(
                Stage.account_id == account_id,
                Stage.stage_number == stage_number
            )
        )
        stage = result.scalar_one_or_none()
        if not stage:
            yield json.dumps({"error": "Stage not found"}) + "\n\n"
            return

        # Get account for context
        account = await db.get(Account, account_id)
        if not account:
            yield json.dumps({"error": "Account not found"}) + "\n\n"
            return

        # Get profile
        demo_profile = None
        
        # 1. Try to match based on account name FIRST (high priority)
        client_lower = account.client_name.lower()
        if "edenred" in client_lower: demo_profile = DEMO_PROFILES["edenred"]
        elif "transmodal" in client_lower: demo_profile = DEMO_PROFILES["transmodal"]
        elif "credifiel" in client_lower: demo_profile = DEMO_PROFILES["credifiel"]
        elif "black" in client_lower and "orange" in client_lower: demo_profile = DEMO_PROFILES["black_and_orange"]
        elif "greenthreads" in client_lower or "moda" in client_lower: demo_profile = DEMO_PROFILES["ecommerce"]
        
        # 2. If no match and a specific profile_key was requested (other than default if we had a match)
        if not demo_profile:
            if profile_key in DEMO_PROFILES:
                demo_profile = DEMO_PROFILES[profile_key]
            else:
                # Dynamic profile fallback
                demo_profile = {
                    "company_name": account.client_name,
                    "profile": f"Empresa: {account.client_name}\nWebsite: {account.company_website}\nIndustria: Desconocida (simulada)\nObjetivo: Crear Buyer Persona"
                }

        # Ensure demo_profile has company_name for simulation
        if "company_name" not in demo_profile:
            demo_profile["company_name"] = account.client_name
        # Enrich with research data if available
        if stage_number == 1 and stage.state and stage.state.get("research_data"):
            r = stage.state.get("research_data")
            demo_profile["profile"] += f"\nIndustria: {r.get('industria')}\nDescripción: {r.get('descripcion_corta')}\nPúblico: {r.get('publico_objetivo_estimado')}"

        # Delays
        delays = {"slow": 2.0, "normal": 0.5, "fast": 0.1}
        delay = delays.get(speed, 0.5)

        conversation_log = []
        iteration = 0
        max_iterations = 60
        
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

        # Get initial message
        if stage_number == 1:
            # Check if research already exists in state
            if not stage.state:
                stage.state = {}
                
            research_data = stage.state.get("research_data")
            if not research_data and account.company_website:
                from app.services import research_service
                try:
                    research_data = await research_service.research_company(account.client_name, account.company_website)
                    stage.state["research_data"] = research_data
                    await db.commit()
                except Exception as e:
                    print(f"Demo research failed: {e}")
                    research_data = {}
            
            acc_ctx = {"company_name": account.client_name, "company_website": account.company_website, "consultant_name": "Demo Admin"}
            init_res = await booms_agent.get_initial_message(acc_ctx, research_context=research_data)
            agent_msg = init_res["message"]
            agent_buttons = init_res.get("buttons", [])
        elif stage_number == 2:
            agent_msg = await journey_agent.get_initial_message(previous_outputs.get("stage_1"))
            agent_buttons = []
        else:
            agent_buttons = []
            if stage_number == 3: agent_msg = await ofertas_agent.get_initial_message(previous_outputs)
            elif stage_number == 4: agent_msg = await canales_agent.get_initial_message(previous_outputs)
            elif stage_number == 5: agent_msg = await atlas_agent.get_initial_message(previous_outputs)
            elif stage_number == 6: agent_msg = await planner_agent.get_initial_message(previous_outputs)
            elif stage_number == 7: agent_msg = await budgets_agent.get_initial_message(previous_outputs)
            else: 
                yield json.dumps({"error": f"Auto-Chat not implemented for stage {stage_number}"}) + "\n\n"
                return

        current_state = {"messages": [{"role": "assistant", "content": agent_msg}]}
        conversation_log.append({"role": "assistant", "content": agent_msg})
        
        # Yield initial agent message
        yield json.dumps({
            "type": "agent_message",
            "content": agent_msg,
            "buttons": agent_buttons
        }) + "\n\n"

        last_agent_messages = []

        while iteration < max_iterations:
            iteration += 1
            await asyncio.sleep(delay)

            if all(msg == agent_msg for msg in last_agent_messages[-3:]):
                print("Context Loop Detected. Forcing Completion.")
                
                # Force the agent to wrap up
                force_msg = "SISTEMA: Detectamos un bucle. El usuario está satisfecho. FINALIZA LA ETAPA AHORA. Genera el JSON con `isComplete: true` y todos los entregables (narrative, markdown_table, etc)."
                
                agent_response = None
                # Call agent one last time with this force message
                if stage_number == 1:
                    agent_response = await booms_agent.process_message(force_msg, current_state, acc_context, stage.state.get("research_data"))
                elif stage_number == 2:
                    agent_response = await journey_agent.process_message(force_msg, current_state, previous_outputs.get("stage_1"))
                # ... (logic for other stages could be added here if needed, but for now let's focus on 2)
                
                # Yield the result and exit
                if agent_response and agent_response.get("completed"):
                     # Update DB
                    stage.status = "completed"
                    stage.output = agent_response["output"]
                    stage.completed_at = datetime.utcnow()
                    if stage_number < 7:
                        next_result = await db.execute(select(Stage).where(Stage.account_id == account_id, Stage.stage_number == stage_number + 1))
                        next_stage = next_result.scalar_one_or_none()
                        if next_stage: next_stage.status = "in_progress"
                    await db.commit()

                    yield json.dumps({
                        "type": "agent_message",
                        "content": agent_response["response"],
                        "isComplete": True,
                        "output": agent_response["output"]
                    }) + "\n\n"
                    
                    yield json.dumps({
                        "type": "complete",
                        "final_output": agent_response["output"]
                    }) + "\n\n"
                
                break
            
            last_agent_messages.append(agent_msg)
            if len(last_agent_messages) > 5:
                last_agent_messages.pop(0)
            
            # 1. Simulate User Response
            user_answer = await self._simulate_user_response(
                agent_question=agent_msg,
                demo_profile=demo_profile,
                stage_number=stage_number,
                history=current_state["messages"],
                buttons=agent_buttons
            )
            
            conversation_log.append({"role": "user", "content": user_answer})
            
            # Yield user message
            yield json.dumps({
                "type": "user_message",
                "content": user_answer
            }) + "\n\n"
            
            # Prepare account context
            acc_context = {
                "company_name": account.client_name,
                "company_website": account.company_website,
                "consultant_name": "Demo Admin"
            }

            # 2. Call Agent
            if stage_number == 1:
                agent_response = await booms_agent.process_message(
                    user_answer, 
                    current_state, 
                    account_context=acc_context,
                    research_context=stage.state.get("research_data")
                )
            elif stage_number == 2:
                agent_response = await journey_agent.process_message(user_answer, current_state, previous_outputs.get("stage_1"))
            elif stage_number == 3:
                agent_response = await ofertas_agent.process_message(user_answer, current_state, previous_outputs)
            elif stage_number == 4:
                agent_response = await canales_agent.process_message(user_answer, current_state, previous_outputs)
            elif stage_number == 5:
                agent_response = await atlas_agent.process_message(user_answer, current_state, previous_outputs)
            elif stage_number == 6:
                agent_response = await planner_agent.process_message(user_answer, current_state, previous_outputs)
            elif stage_number == 7:
                agent_response = await budgets_agent.process_message(user_answer, current_state, previous_outputs)
            
            agent_msg = agent_response["response"]
            agent_buttons = agent_response.get("buttons", [])
            current_state = agent_response["state"]
            conversation_log.append({"role": "assistant", "content": agent_msg})
            
            # Yield agent response
            yield json.dumps({
                "type": "agent_message",
                "content": agent_msg,
                "buttons": agent_buttons,
                "confidenceScore": agent_response.get("confidenceScore"),
                "progressLabel": agent_response.get("progressLabel"),
                "progressStep": agent_response.get("progressStep")
            }) + "\n\n"
            
            # Update DB periodically or at the end
            stage.state = current_state
            
            if agent_response["completed"]:
                stage.status = "completed"
                stage.output = agent_response["output"]
                stage.completed_at = datetime.utcnow()
                
                # Unlock next stage
                if stage_number < 7:
                    next_result = await db.execute(select(Stage).where(Stage.account_id == account_id, Stage.stage_number == stage_number + 1))
                    next_stage = next_result.scalar_one_or_none()
                    if next_stage:
                        next_stage.status = "in_progress"
                
                await db.commit()
                yield json.dumps({
                    "type": "complete",
                    "final_output": agent_response["output"]
                }) + "\n\n"
                return
            
            await db.commit()

    async def _simulate_user_response(
        self,
        agent_question: str,
        demo_profile: Dict[str, Any],
        stage_number: int,
        history: List[Dict[str, str]],
        buttons: List[str] = []
    ) -> str:
        
        # Determine the company/persona based on the account name/website from the profile dict
        # In a real dynamic scenario, we trust the profile dict passed in which now contains real company info
        company_name = demo_profile.get('company_name', 'TechFlow CRM')
        company_context = demo_profile.get('profile', '')
        
        buttons_context = f"\nOpciones de respuesta rápida disponibles: {', '.join(buttons)}" if buttons else ""
        
        prompt = f"""
        Eres el cliente ideal (Buyer Persona) de la empresa **{company_name}**.
        
        **Tu Contexto:**
        {company_context}
        
        **Instrucciones:**
        Estás hablando con un consultor (el Agente AI) que te está entrevistando para crear tu perfil de cliente ideal.
        
        1. Responde a la pregunta del agente basándote en la información de tu empresa ({company_name}).
        2. Si la empresa es real (como Uber, Apple, una pizzería local), **ACTÚA COMO TAL**. Inventa detalles realistas si es necesario pero mantente fiel a la industria.
        3. Si te da opciones (botones), elige la que mejor encaje, o responde con tu propia voz si ninguna encaja perfecto.
        4. Sé conciso pero da información valiosa.
        5. Tienes un tono profesional pero directo.
        
        {buttons_context}
        
        **Pregunta del Agente:**
        {agent_question}
        
        **Tu Respuesta:**
        """
        
        # We use the same ai_provider_service but we could force a specific model for simulation
        response = await ai_provider_service.chat_completion(
            messages=[
                {"role": "system", "content": f"Eres el Director de Marketing o Dueño de {company_name}."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.strip()
