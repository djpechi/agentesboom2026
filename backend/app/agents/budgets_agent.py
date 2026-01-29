# /backend/app/agents/budgets_agent.py
"""
Budgets Agent (Media Planner)
Stage 7 - Generates Media Plan and Investment Forecasting
"""

from typing import Any
from app.services import ai_provider_service

SYSTEM_PROMPT_TEMPLATE = """
# IDENTIDAD Y ROL

Eres Budgets, el Director Financiero de Marketing de BOOMS.
Tu trabajo es tomar la estrategia creativa y ponerle números reales.
Garantizas que cada dólar invertido tenga un propósito y un retorno esperado.

# CONTEXTO DISPONIBLE

**Presupuesto Total (Estimado):**
{budget_limit}

**Canales Prioritarios (Agente 4):**
{channels_matrix}

**Precio Oferta (Agente 3):**
{offer_price}

# PROCESO (3 Fases)

## FASE 1: Benchmarks de Mercado (Investigación)
Investiga los costos actuales.
- Busca: "Average CPC [Channel] B2B [Industry] 2024".
- Busca tasas de conversión promedio.

## FASE 2: Distribución de Presupuesto (Allocation)
Divide el dinero disponible.
- Regla 70/20/10:
  - 70% en Canales Probados (Los "Bullseye").
  - 20% en Canales Seguros (Retargeting, Email).
  - 10% en Experimentos.

## FASE 3: Proyección (Forecasting)
Calcula qué obtendrá el cliente.
- Impressions = Budget / CPM * 1000
- Clicks = Impressions * CTR
- Leads = Clicks * Conv. Rate
- Ventas Estimadas = Leads * Close Rate
- ROAS Estimado.

# FORMATO DE RESPUESTA (JSON)

SIEMPRE responde en JSON para mantener el estado.

{{
  "agentMessage": "Texto para el usuario...",
  "state": {{
    "currentPhase": "benchmarks | allocation | forecasting",
    "collectedData": {{ ... }}
  }},
  "completed": false, // true solo al final
  "output": null
}}

Sé conservador en tus estimaciones. Es mejor prometer de menos y entregar de más.
"""

async def process_message(
    message: str,
    state: dict[str, Any],
    previous_stage_outputs: dict[str, Any] | None = None,
    ai_model: str | None = None
) -> dict[str, Any]:
    """
    Process a user message through the Budgets agent
    """
    messages = state.get("messages", [])
    
    # Context summarization
    budget_limit = "N/A"
    channels_matrix = "N/A"
    offer_price = "N/A"
    
    if previous_stage_outputs:
        s3 = previous_stage_outputs.get("stage_3", {})
        s4 = previous_stage_outputs.get("stage_4", {})
        
        if s4:
            channels_matrix = str(s4.get("channel_matrix", "N/A"))
            budget_limit = str(s4.get("budget", "N/A")) # Assuming budget was collected in S4
            if budget_limit == "N/A":
                 # Fallback if not found in output, user might mention it now
                 pass
            
        if s3 and "final_offer" in s3:
             offer_price = str(s3.get("final_offer", {}).get("Price", "N/A"))

    # Initialize conversation
    if not messages:
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            budget_limit=budget_limit,
            channels_matrix=channels_matrix,
            offer_price=offer_price
        )
        messages = [{"role": "system", "content": system_prompt}]

    messages.append({"role": "user", "content": message})

    try:
        selected_model = ai_model if ai_model else "gemini-2.0-flash"
        
        response = await ai_provider_service.chat_completion(
            messages=messages,
            model_override=selected_model,
            temperature=0.7
        )

        messages.append({"role": "assistant", "content": response})

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
        raise Exception(f"Error in Budgets agent: {str(e)}")

async def get_initial_message(previous_stage_outputs: dict[str, Any] | None = None) -> str:
    return """¡Hola! Soy Budgets 💰. El último paso.

Hemos creado una oferta (S3), elegido canales (S4), diseñado una estrategia SEO (S5) y un calendario (S6).
Ahora vamos a ponerle precio a todo esto para que sea rentable.

Necesito confirmar tu **Presupuesto Total de Pauta (Ads)** para los próximos 3 meses.
¿Sigues cómodo con la cifra que discutimos antes, o quieres ajustar algo antes de que haga las proyecciones?"""
