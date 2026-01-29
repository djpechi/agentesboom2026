# /backend/app/agents/journey_agent.py
"""
Journey Agent (Stage 2) - Architect of the Buyer's Journey
Aligned with Agente2.md spec.
Enforces strict sequential logic to avoid loops.
"""

from typing import Any, Dict, List, Optional
import json
from app.services import ai_provider_service

STAGES_ORDER = ["awareness", "consideration", "decision", "delight"]

SYSTEM_PROMPT = """# Role and Objective
Eres el **Arquitecto BOOMS del Buyer’s Journey**.
Tu objetivo: Construir el Journey Map (Narrativa + Tabla).
Tu regla de oro: **AVANZAR**. No te quedes estancado profundizando infinitamente en una etapa.

# Stage Instructions
Estás guiando al usuario por estas etapas estrictamente en orden:
1. **Awareness**: ¿Cómo descubren el problema? (Triggers, síntomas)
2. **Consideration**: ¿Qué soluciones evalúan? (Investigación, competidores)
3. **Decision**: ¿Por qué te eligen a ti? (Criterios, diferenciadores)
4. **Delight**: Post-compra y fidelización.

# Interaction Rules
- **MAXIMO 2-3 INTERACCIONES POR ETAPA**.
- Una vez obtengas los datos básicos (Triggers, Canales, Criterios), **PASA DE INMEDIATO A LA SIGUIENTE ETAPA**.
- **PROHIBIDO**: Preguntar "¿Quieres profundizar más?" o "¿Hay algo más?".
- **OBLIGATORIO**: Si tienes la info, di: "Perfecto. Pasemos a la etapa [SIGUIENTE ETAPA]. Mis preguntas son..."
- **SUPERIOR**: Si ves un mensaje de "SISTEMA: FINALIZA LA ETAPA AHORA", ignora todo lo demás y genera el JSON final inmediatamente con `isComplete: true`.

# Output Format (JSON)
SIEMPRE responde en JSON.

```json
{
  "agentMessage": "Texto de respuesta al usuario...",
  "progress": <0-100 integer>,
  "isComplete": <boolean>,
  "currentState": {
    "stage": "<awareness|consideration|decision|delight|finished>",
    "step_index": <0-3 integer>
  },
  "output": <null or final object>
}
```

Cuando `isComplete` sea true (al finalizar Delight), rellena `output` con:
```json
{
  "narrative": "...",
  "markdown_table": "| Etapa | ... |",
  "csv_block": "...",
  "hubspot_props": [...]
}
```
"""

async def process_message(
    message: str,
    state: Dict[str, Any],
    previous_stage_output: Optional[Dict[str, Any]] = None,
    ai_model: Optional[str] = None
) -> Dict[str, Any]:
    
    # 1. State Recovery & Management
    history = state.get("messages", [])
    journey_state = state.get("journey_state", {})
    
    # Default State
    current_stage = journey_state.get("stage", "awareness")
    turn_count_in_stage = journey_state.get("turn_count", 0)
    
    # Identify stage index
    try:
        stage_idx = STAGES_ORDER.index(current_stage)
    except ValueError:
        stage_idx = 0
        current_stage = "awareness"

    # 2. Initialize history if empty
    if not history:
        # Inject Stage 1 Context
        persona_context = ""
        if previous_stage_output:
            bp = previous_stage_output.get("buyerPersona", {})
            if isinstance(bp, dict):
                name = bp.get("name", "Buyer Persona")
                narrative = bp.get("narrative", "N/A")
                persona_context = f"BUYER PERSONA (STAGE 1):\nNombre: {name}\nResumen: {narrative}\n"
        
        full_system_prompt = SYSTEM_PROMPT + "\n\nCONTEXTO INICIAL:\n" + persona_context
        history = [{"role": "system", "content": full_system_prompt}]
        turn_count_in_stage = 0

    # 3. User Message Handling
    history.append({"role": "user", "content": message})
    turn_count_in_stage += 1
    
    # 4. Forced Progression Logic
    # If we have spent > 2 turns in this stage, FORCE the agent to move on.
    system_injection = None
    if turn_count_in_stage >= 3:
        if stage_idx < len(STAGES_ORDER) - 1:
            next_stage = STAGES_ORDER[stage_idx + 1]
            system_injection = f"SISTEMA: Ya has discutido suficiente la etapa {current_stage}. OBLIGATORIO: Resume y pasa INMEDIATAMENTE a la etapa {next_stage}. Haz las preguntas de {next_stage}."
        else:
            system_injection = "SISTEMA: Ya has cubierto todas las etapas. OBLIGATORIO: Genera el JSON final con `isComplete: true` y todos los entregables (narrative, table, csv)."

    if system_injection:
        history.append({"role": "system", "content": system_injection})

    # 5. Call LLM
    try:
        response_text = await ai_provider_service.chat_completion(
            messages=history,
            temperature=0.7,
            model_override=ai_model
        )
        
        # 6. Parse JSON
        clean_text = response_text.strip()
        start_idx = clean_text.find('{')
        end_idx = clean_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            data = json.loads(clean_text[start_idx:end_idx+1])
            
            # Extract fields
            agent_msg = data.get("agentMessage") or data.get("message") or "..."
            new_stage_state = data.get("currentState", {})
            new_stage = new_stage_state.get("stage", current_stage)
            is_complete = data.get("isComplete", False)
            
            # Logic: Did the agent actually move stage?
            # If the LLM says it moved stage, reset turn count.
            # If strictly forcefully moved by system, accept it.
            
            real_next_stage = new_stage
            real_turn_count = turn_count_in_stage
            
            if new_stage != current_stage:
                # Stage changed
                real_turn_count = 0
            
            # Construct new state
            final_journey_state = {
                "stage": real_next_stage,
                "turn_count": real_turn_count,
                "data": new_stage_state.get("journeyData", [])
            }
            
            new_state = state.copy()
            new_state["messages"] = history + [{"role": "assistant", "content": response_text}]
            new_state["journey_state"] = final_journey_state
            
            return {
                "response": agent_msg,
                "state": new_state,
                "completed": is_complete,
                "output": data.get("output"),
                "confidenceScore": 100 if is_complete else 50
            }
            
        else:
            return {
                "response": response_text,
                "state": {"messages": history + [{"role": "assistant", "content": response_text}]},
                "completed": False,
                "output": None
            }

    except Exception as e:
        return {
            "response": "Error procesando. Intenta de nuevo.",
            "state": state,
            "completed": False
        }

async def get_initial_message(previous_stage_output: Optional[Dict[str, Any]] = None) -> str:
    brand = "tu marca"
    persona = "el Buyer Persona"
    if previous_stage_output:
        brand = previous_stage_output.get("brand_name", brand)
        bp = previous_stage_output.get("buyerPersona", {})
        if isinstance(bp, dict):
            persona = bp.get("name", persona)
            
    return f"¡Hola! Soy tu Arquitecto de Journey. Vamos a crear el mapa para **{persona}** de **{brand}**.\n\nFase 1: **Awareness**. ¿Qué detona que {persona} busque una solución? (Dime 1-2 triggers principales)."
