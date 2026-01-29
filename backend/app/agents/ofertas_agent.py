# /backend/app/agents/ofertas_agent.py
"""
Ofertas Agent (100M Offers & StoryBrand)
Stage 3 - Creates irresistible offers using Hormozi and StoryBrand frameworks via RAG
"""

from typing import Any
from app.services import ai_provider_service, rag_service

SYSTEM_PROMPT_TEMPLATE = """
# IDENTIDAD Y ROL

Eres el experto en Ofertas Irresistibles de BOOMS. Tu personalidad es una mezcla de Alex Hormozi (directo, enfocado en valor) y Donald Miller (claro, enfocado en narrativa).

Tu objetivo es ayudar al usuario a construir una "Oferta de $100M" que sea imposible de rechazar, basándote en los datos del Buyer Persona (Agente 1) y su Journey (Agente 2).

# CONTEXTO DISPONIBLE

**Buyer Persona (Resumen):**
{buyer_persona_summary}

**Industria/Negocio:**
{industry_context}

**EXPERT KNOWLEDGE (RAG):**
{rag_context}

# PROCESO (3 Fases)

## FASE 1: La Ecuación de Valor (Hormozi)
Nos enfocamos en maximizar el valor percibido.
1. **Dream Outcome**: Clarificar el resultado soñado.
2. **Perceived Likelihood**: Aumentar certeza de éxito.
3. **Time Delay**: Reducir tiempo a resultados.
4. **Effort & Sacrifice**: Reducir esfuerzo.

## FASE 2: StoryBrand (Claridad)
Definimos el mensaje usando el framework SB7 (Character, Problem, Guide, Plan, Call to Action, Success, Failure).

## FASE 3: El Stack de la Oferta
Construimos la oferta final con Core Offer, Bonuses, Guarantees, Scarcity/Urgency y Naming.

# FORMATO DE RESPUESTA (JSON)

SIEMPRE responde en JSON para mantener el estado.

{{
  "agentMessage": "Texto para el usuario...",
  "state": {{
    "currentPhase": "value_equation | storybrand | offer_stack",
    "collectedData": {{ ... }}
  }},
  "completed": false, // true solo al final
  "output": {{  // SOLO al final (completed=true)
    "value_equation": {{
      "dream_outcome": "...",
      "perceived_likelihood": "...",
      "time_delay": "...",
      "effort_sacrifice": "..."
    }},
    "storybrand": {{
      "character": "...",
      "problem": "...",
      "guide": "...",
      "plan": "...",
      "call_to_action": "...",
      "success": "...",
      "failure": "..."
    }},
    "offer_stack": {{
      "core_offer": "...",
      "bonuses": ["bonus 1", "bonus 2"],
      "guarantees": ["guarantee 1"],
      "scarcity_urgency": "...",
      "naming": "Nombre de la Oferta"
    }}
  }}
}}

Sé conversacional, haz 1-2 preguntas a la vez para avanzar en las fases. No abrumes.
"""

async def process_message(
    message: str,
    state: dict[str, Any],
    previous_stage_outputs: dict[str, Any] | None = None,
    ai_model: str | None = None
) -> dict[str, Any]:
    """
    Process a user message through the Ofertas agent
    """
    # Get message history from state
    messages = state.get("messages", [])
    
    # Get RAG context if not already loaded (or reload it)
    # Ideally we'd cache this or pass it in system prompt once
    rag_context = await rag_service.get_knowledge_context(["100m_offers.txt", "storybrand.txt"])

    # Prepare context summaries
    buyer_persona_summary = "N/A"
    industry_context = "N/A"
    
    if previous_stage_outputs:
        # Extract meaningful summary from Stage 1 & 2 outputs
        # Assuming Stage 1 output has 'brand_name', 'industry', 'target_audience'
        s1 = previous_stage_outputs.get("stage_1", {})
        buyer_persona_summary = f"Audience: {s1.get('target_audience', 'Unknown')}\nPain Points: {s1.get('pain_points', 'Unknown')}" # Adapt based on actual output structure
        industry_context = f"Brand: {s1.get('brand_name', 'Unknown')}\nIndustry: {s1.get('industry', 'Unknown')}"

    # Add system prompt if first message
    if not messages:
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            buyer_persona_summary=buyer_persona_summary,
            industry_context=industry_context,
            rag_context=rag_context
        )
        messages = [{"role": "system", "content": system_prompt}]

    # Add user message
    messages.append({"role": "user", "content": message})

    try:
        # Use AI Provider (Use account model or fallback to gemini for large RAG context)
        selected_model = ai_model if ai_model else "gemini-2.0-flash"
        
        response = await ai_provider_service.chat_completion(
            messages=messages,
            model_override=selected_model,
            temperature=0.7
        )

        messages.append({"role": "assistant", "content": response})

        # Parse JSON response
        import json
        
        # Simple extraction logic (robustness like in other agents)
        completed = False
        output = None
        current_state_data = {}
        
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                response_data = json.loads(json_str)
                
                # Check completion status from JSON
                completed = response_data.get("completed", False)
                output = response_data.get("output")
                
                # Update internal state tracking
                if "state" in response_data:
                    current_state_data = response_data["state"]
                    
                # Use the agentMessage for the chat UI if it exists, otherwise use full response
                if "agentMessage" in response_data:
                    # We might want to store the clean message in history, but for now we store full JSON response
                    # to keep state persistence simple in this stateless architecture
                    pass
        except json.JSONDecodeError:
            pass

        return {
            "response": response, # Return full response, frontend parses or displays
            "state": {"messages": messages, "agent_data": current_state_data},
            "completed": completed,
            "output": output
        }

    except Exception as e:
        raise Exception(f"Error in Ofertas agent: {str(e)}")

async def get_initial_message(previous_stage_outputs: dict[str, Any] | None = None) -> str:
    """Get the agent's initial greeting message"""
    return """¡Hola! Soy tu experto en Ofertas Irresistibles ($100M Offers). 💸

He analizado tu Buyer Persona y tu Journey. Ahora vamos a construir una oferta tan buena que tus clientes se sentirán estúpidos al decir que no.

Vamos a trabajar en 3 fases:
1.  **La Ecuación de Valor**: Maximizar lo que entregas.
2.  **StoryBrand**: Clarificar tu mensaje.
3.  **El Stack**: Crear los bonus y garantías.

Para empezar, hablemos del **Resultado Soñado (Dream Outcome)** de tu cliente.
¿Cuál es la transformación final REAL que buscan? (No me digas "software", dime "libertad de tiempo" o "duplicar ingresos")."""
