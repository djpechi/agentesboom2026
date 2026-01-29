# /backend/app/agents/atlas_agent.py
"""
Atlas Agent (AEO Strategist)
Stage 5 - SEO/AEO Content Strategy using Perplexity for keyword research
"""

from typing import Any
from app.services import ai_provider_service

SYSTEM_PROMPT_TEMPLATE = """
# IDENTIDAD Y ROL

Eres Atlas, el Estratega de AEO (Answer Engine Optimization) de BOOMS.
Tu misión no es solo posicionar en Google (SEO clásico), sino asegurar que tu marca sea la "respuesta recomendada" por inteligencias artificiales como ChatGPT, Perplexity y Gemini.

# CONTEXTO DISPONIBLE

**Buyer Persona:**
{buyer_persona_summary}

**Oferta:**
{offer_summary}

**Canales Pautados:**
{channels_summary}

**Industria/Negocio:**
{industry_context}

# PROCESO (3 Fases)

## FASE 1: Pilares de Contenido (Authority)
Definimos los 3-5 grandes temas donde la marca debe ser indiscutible autoridad.
- Basado en los Pain Points del Buyer (Agente 1).
- Basado en los "Sueños" de la Oferta (Agente 3).

## FASE 2: Topic Clusters & Keywords (Investigación)
Investiga activamente qué está preguntando la gente.
- Usa tu herramienta para buscar: "Preguntas frecuentes sobre [Tema] en [Industria]".
- Identifica "Low hanging fruit" (Keywords de cola larga con intención de convertir).
- Agrupa temas en Clusters: Página Pilar + Posts de soporte.

## FASE 3: Optimización AEO
Para cada pilar, define cómo estructurar la respuesta para IA.
- Formato Q&A.
- Datos estructurados (Schema).
- Claridad y autoridad.

# FORMATO DE RESPUESTA (JSON)

SIEMPRE responde en JSON para mantener el estado.

{{
  "agentMessage": "Texto para el usuario...",
  "state": {{
    "currentPhase": "pillars | clusters | aeo_strategy",
    "collectedData": {{ ... }}
  }},
  "completed": false, // true solo al final
  "output": null
}}

Sé técnico pero explica el porqué ("Hacemos esto para que ChatGPT te cite").
"""

async def process_message(
    message: str,
    state: dict[str, Any],
    previous_stage_outputs: dict[str, Any] | None = None,
    ai_model: str | None = None
) -> dict[str, Any]:
    """
    Process a user message through the Atlas agent
    """
    messages = state.get("messages", [])
    
    # Context summarization
    buyer_persona_summary = "N/A"
    offer_summary = "N/A"
    channels_summary = "N/A"
    industry_context = "N/A"
    
    if previous_stage_outputs:
        s1 = previous_stage_outputs.get("stage_1", {})
        s3 = previous_stage_outputs.get("stage_3", {})
        s4 = previous_stage_outputs.get("stage_4", {})
        
        industry_context = f"Brand: {s1.get('brand_name', 'Unknown')}\nIndustry: {s1.get('industry', 'Unknown')}"
        buyer_persona_summary = f"Target: {s1.get('target_audience', 'Unknown')}"
        
        if s3 and "final_offer" in s3:
             offer_summary = str(s3["final_offer"])
        if s4 and "channel_matrix" in s4:
             channels_summary = str(s4["channel_matrix"])

    # Initialize conversation
    if not messages:
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            buyer_persona_summary=buyer_persona_summary,
            offer_summary=offer_summary,
            channels_summary=channels_summary,
            industry_context=industry_context
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
        raise Exception(f"Error in Atlas agent: {str(e)}")

async def get_initial_message(previous_stage_outputs: dict[str, Any] | None = None) -> str:
    return """¡Hola! Soy Atlas 🌍. Vamos a hacer que tu marca sea la respuesta.

El SEO ha cambiado. Ya no basta con aparecer en Google; ahora tu cliente le pregunta a ChatGPT, Gemini o Perplexity. Y si ellos no te citan, no existes.

Mi trabajo es construir tu **Autoridad Temática**.

Para la **Fase 1**, necesito saber:
1.  Si tuvieras que escribir un libro sobre tu industria, ¿cuáles serían los 3 capítulos principales? (Esos serán tus Pilares).
2.  ¿Qué preguntas sientes que tu cliente NO encuentra respondidas correctamente en internet hoy?"""
