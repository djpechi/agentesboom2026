# /backend/app/agents/canales_agent.py
"""
Canales Agent (Channel Strategist)
Stage 4 - Selects and prioritizes marketing channels using Perplexity for market data
"""

from typing import Any, List, Dict
from app.services import ai_provider_service

SYSTEM_PROMPT_TEMPLATE = """
# IDENTIDAD Y ROL

Eres el Estratega de Canales de BOOMS. Tu trabajo es decir "NO" a la mayoría de los canales para enfocar los recursos del cliente en los 2-3 canales que realmente funcionarán.

Basas tus decisiones en DATOS (que buscarás activamente), no en suposiciones.

# CONTEXTO DISPONIBLE

**Buyer Persona (Resumen):**
{buyer_persona_summary}

**Oferta (Resumen):**
{offer_summary}

**Industria/Negocio:**
{industry_context}

# PROCESO (3 Fases)

## FASE 1: Restricciones y Activos (Discovery)
Antes de sugerir, entendemos con qué contamos.
1. **Presupuesto**: ¿Cuánto hay para invertir mensualmente?
2. **Equipo**: ¿Quién va a operar? (¿Agencia, In-house, Fundador solo?)
3. **Activos**: ¿Tienen ya listas de correo, seguidores, web con tráfico?
4. **Tiempo**: ¿Necesitan resultados mañana o construyen a largo plazo?

## FASE 2: Investigación de Mercado (Investigación)
**AQUÍ ES DONDE BRILLAS.**
Cuando tengas los datos de la Fase 1, avisa al usuario que vas a investigar.
Usa tu "herramienta" (simulada aquí por tu conocimiento o tool calls si están activos) para validar:
- Costos (CPC/CPM) reales en la industria.
- Dónde está la atención del Buyer Persona.

## FASE 3: La Matriz de Decisión
Recomienda la estrategia final.
- **Canales Primarios (Bullseye)**: 1-2 canales imprescindibles.
- **Canales Secundarios**: Para expansión.
- **Canales a Evitar**: Explica por qué NO usarlos.

# FORMATO DE RESPUESTA (JSON)

SIEMPRE responde en JSON para mantener el estado.

{{
  "agentMessage": "Texto para el usuario...",
  "state": {{
    "currentPhase": "discovery | research | strategy",
    "collectedData": {{ ... }}
  }},
  "completed": false, // true solo al final
  "output": null
}}

Sé directo y estratégico. No des respuestas genéricas.
"""

async def process_message(
    message: str,
    state: dict[str, Any],
    previous_stage_outputs: dict[str, Any] | None = None,
    ai_model: str | None = None
) -> dict[str, Any]:
    """
    Process a user message through the Canales agent
    """
    messages = state.get("messages", [])
    
    # Context summarization
    buyer_persona_summary = "N/A"
    offer_summary = "N/A"
    industry_context = "N/A"
    
    if previous_stage_outputs:
        # Extract summaries (simplified logic)
        s1 = previous_stage_outputs.get("stage_1", {})
        s3 = previous_stage_outputs.get("stage_3", {})
        
        industry_context = f"Brand: {s1.get('brand_name', 'Unknown')}\nIndustry: {s1.get('industry', 'Unknown')}"
        buyer_persona_summary = f"Target: {s1.get('target_audience', 'Unknown')}"
        
        if s3 and "final_offer" in s3:
             offer_summary = str(s3["final_offer"])

    # Initialize conversation
    if not messages:
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            buyer_persona_summary=buyer_persona_summary,
            offer_summary=offer_summary,
            industry_context=industry_context
        )
        messages = [{"role": "system", "content": system_prompt}]

    messages.append({"role": "user", "content": message})

    try:
        # Check if we need to trigger "Research Mode" (Simulated/Real Perplexity)
        # In this implementation, we use the standard model but instruct it to act as if researching
        # ideally we would switch models or parameters here if using Perplexity API specifically
        
        selected_model = ai_model if ai_model else "gemini-2.0-flash"
        
        response = await ai_provider_service.chat_completion(
            messages=messages,
            model_override=selected_model,
            temperature=0.7
        )

        messages.append({"role": "assistant", "content": response})

        # JSON parsing logic
        import json
        completed = False
        output = None
        current_state_data = {}
        
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                response_data = json.loads(json_str)
                completed = response_data.get("completed", False)
                output = response_data.get("output")
                if "state" in response_data:
                    current_state_data = response_data["state"]
        except json.JSONDecodeError:
            pass

        return {
            "response": response,
            "state": {"messages": messages, "agent_data": current_state_data},
            "completed": completed,
            "output": output
        }

    except Exception as e:
        raise Exception(f"Error in Canales agent: {str(e)}")

async def get_initial_message(previous_stage_outputs: dict[str, Any] | None = None) -> str:
    return """¡Hola! Soy tu Estratega de Canales. 🎯

Ya sé a quién le vendes (Agente 1) y qué les vendes (Agente 3). Ahora vamos a definir **dónde** poner tu dinero para que vuelva multiplicado.

Mi trabajo es decirte NO a la mayoría de las cosas y enfocarnos en lo que sí funciona.

Para empezar la **Fase de Discovery**, cuéntame sobre tus recursos:
1.  **Presupuesto Mensual** aproximado para pauta/marketing.
2.  **Equipo Disponible** (¿Eres solo tú, tienes equipo in-house, o agencia?)."""
