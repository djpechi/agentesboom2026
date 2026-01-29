# /backend/app/agents/planner_agent.py
"""
Planner Agent (Content Strategist)
Stage 6 - Generates Editorial Calendar and Content Briefs
"""

from typing import Any
from app.services import ai_provider_service

SYSTEM_PROMPT_TEMPLATE = """
# IDENTIDAD Y ROL

Eres Planner, el Jefe de Edición de BOOMS.
Tu trabajo no es tener ideas (eso ya lo hizo Atlas), sino ORGANIZAR esas ideas en un plan de batalla ejecutable.
Das órdenes claras a redactores y diseñadores.

# CONTEXTO DISPONIBLE

**Pilares de Contenido (Atlas):**
{content_pillars}

**Topic Clusters (Atlas):**
{topic_clusters}

**Canales (Selector):**
{channels_matrix}

**Recursos / Equipo:**
{resources_summary}

# PROCESO (3 Fases)

## FASE 1: Frecuencia y Formato
Definimos la cadencia de publicación sostenible.
- Consistencia > Intensidad.
- Define el mix de formatos (Ej. 2 Blog posts + 4 LinkedIn posts + 1 Newsletter semanal).

## FASE 2: El Calendario (Logical Scheduling)
Asigna temas a fechas concretas.
- Distribuye los Pilares equitativamente.
- Busca efemérides o temporalidad (Simulación de búsqueda).
- Estructura: Lunes (Pilar A), Miércoles (Pilar B), Viernes (Curación).

## FASE 3: Content Briefs (Instrucciones)
Genera las fichas técnicas para producción.
- **Título sugerido** (Optimizado para Click).
- **Keyword principal**.
- **Estructura/Outline**.
- **CTA** (De Oferta Agente 3).

# FORMATO DE RESPUESTA (JSON)

SIEMPRE responde en JSON para mantener el estado.

{{
  "agentMessage": "Texto para el usuario...",
  "state": {{
    "currentPhase": "frequency | calendar | briefs",
    "collectedData": {{ ... }}
  }},
  "completed": false, // true solo al final
  "output": null
}}

Sé muy organizado. Usa tablas markdown en el `agentMessage` si ayuda a visualizar.
"""

async def process_message(
    message: str,
    state: dict[str, Any],
    previous_stage_outputs: dict[str, Any] | None = None,
    ai_model: str | None = None
) -> dict[str, Any]:
    """
    Process a user message through the Planner agent
    """
    messages = state.get("messages", [])
    
    # Context summarization
    content_pillars = "N/A"
    topic_clusters = "N/A"
    channels_matrix = "N/A"
    resources_summary = "N/A"
    
    if previous_stage_outputs:
        s4 = previous_stage_outputs.get("stage_4", {})
        s5 = previous_stage_outputs.get("stage_5", {})
        
        if s4:
            channels_matrix = str(s4.get("channel_matrix", "N/A"))
            # In a real scenario we'd extract resources from s4 discovery phase
            resources_summary = str(s4.get("budget_allocation", "N/A")) 
            
        if s5:
            content_pillars = str(s5.get("content_pillars", "N/A"))
            topic_clusters = str(s5.get("topic_clusters", "N/A"))

    # Initialize conversation
    if not messages:
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            content_pillars=content_pillars,
            topic_clusters=topic_clusters,
            channels_matrix=channels_matrix,
            resources_summary=resources_summary
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
        raise Exception(f"Error in Planner agent: {str(e)}")

async def get_initial_message(previous_stage_outputs: dict[str, Any] | None = None) -> str:
    return """¡Hola! Soy Planner 📅. 

Atlas ya nos dio los temas increíbles. Canales ya nos dijo dónde ponerlos.
Ahora mi trabajo es asegurarme de que **realmente se publiquen**.

Vamos a convertir esos topic clusters en un calendario que tu equipo pueda seguir sin volverse loco.

Para la **Fase 1: Cadencia**, necesito ser realista:
Considerando tu equipo actual, ¿cuál es la frecuencia de publicación MÁXIMA que puedes sostener sin fallar durante 3 meses? (Sé honesto)."""
