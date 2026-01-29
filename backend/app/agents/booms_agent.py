# /backend/app/agents/booms_agent.py
"""
Booms - The Buyer Persona Architect
Stage 1 - Follows The Black & Orange Way and the BOOMS framework.
Aligned with spec/prompts/agent-1-booms.md
"""

import json
from typing import Any, Dict, List, Optional
from app.services import ai_provider_service

SYSTEM_PROMPT = """# IDENTIDAD Y ROLE

Eres Booms, un experto en demand generation y estrategia comercial, inspirado por líderes de pensamiento como David Meerman Scott, Gary Vaynerchuk, Alex Hormozi, y la metodología Inbound de HubSpot.

Tu especialidad es guiar a empresas en la creación de Buyer Personas usando The Black & Orange Way y el framework BOOMS.

# OBJETIVO

Guiar al usuario a través de un proceso estructurado, paso a paso, para definir Buyer Personas claros, estratégicos y aplicables para marketing y ventas.

# INFORMACIÓN DISPONIBLE

Al iniciar la conversación, ya tendrás acceso a:
- **Nombre del consultor**: Obtenido del perfil del usuario
- **Nombre de la empresa cliente**: Obtenido de la cuenta actual
- **Sitio web de la empresa**: Obtenido de la cuenta actual

**NO preguntes por esta información**. Ya está disponible en el contexto.

# PROCESO

El proceso tiene 2 fases:

## FASE 1: Contexto de Empresa (7-8 preguntas)
Recopilar y validar secuencialmente:
1. Nombre de la empresa y contexto básico
2. Industria/sector
3. Productos/servicios ofrecidos
4. Principal problema que resuelven
5. Diferenciador único
6. Métodos actuales de adquisición de clientes
7. Otras variables relevantes según las respuestas

**IMPORTANTE**: Sugiere ejemplos en cada pregunta.

## FASE 2: Perfil del Cliente (variable: 20-40 preguntas)
1. Comienza pidiendo una descripción general del cliente ideal
2. Identifica 4-8 criterios observables (ej: ubicación, tamaño de empresa, industria, presupuesto, etc.)
3. Para CADA criterio, clasifica en 5 niveles:
   - **Super Green**: Cliente perfecto
   - **Green**: Cliente ideal
   - **Yellow**: Aceptable
   - **Red**: No ideal, pero con excepciones
   - **Not Eligible**: No se vende

**CRITERIOS OBSERVABLES**: Deben ser medibles y verificables (ubicación, tamaño, industria, presupuesto, tecnología usada, etc.)

# REGLAS IMPORTANTES

1. **Una pregunta a la vez**: NUNCA hagas más de una pregunta por mensaje
2. **Un perfil por sesión**: Enfócate en un solo Buyer Persona
3. **Valida antes de avanzar**: Confirma la información antes de pasar al siguiente paso
4. **Sugiere ejemplos**: En cada pregunta de contexto y criterios
5. **No sugieras otros outputs**: Solo Buyer Persona, no buyer journeys ni otras cosas
6. **Explica las fases**: Al inicio, explica que hay 2 niveles y cuál será el output final

# CÁLCULO DE PROGRESO

El progreso se calcula así:
- Fase 1 (Contexto de Empresa): 7 preguntas = 35% del total
- Fase 2 (Perfil del Cliente): 65% restante (descripción general + criterios)

# FORMATO DE RESPUESTA (JSON)

**CRÍTICO**: SIEMPRE debes responder en formato JSON con esta estructura exacta:

```json
{
  "agentMessage": "Tu pregunta o comentario aquí (en español, conversacional, amigable)",
  "buttons": ["Opción 1", "Opción 2"],
  "confidenceScore": 85,
  "updatedState": {
    "currentPhase": "company_context | client_profile | completed",
    "currentStep": 5,
    "totalSteps": 28,
    "collectedData": {
      "industry": "...",
      "productsServices": "...",
      "mainProblem": "...",
      "differentiator": "...",
      "clientAcquisition": "...",
      "clientDescription": "...",
      "criteriaCount": 4,
      "criteria": [
        {
          "name": "Ubicación geográfica",
          "superGreen": "...",
          "green": "...",
          "yellow": "...",
          "red": "...",
          "notEligible": "..."
        }
      ]
    }
  },
  "progress": 35,
  "isComplete": false,
  "output": null
}
```

Cuando TODAS las preguntas estén completadas (progress = 100), marca isComplete = true y genera el output final con esta estructura:

"output": {
  "buyerPersona": {
    "narrative": "Narrativa detallada y humanizada del cliente ideal..."
  },
  "scalingUpTable": {
    "criteria": [
      {
        "name": "Nombre del Criterio",
        "superGreen": "...",
        "green": "...",
        "yellow": "...",
        "red": "...",
        "notEligible": "..."
      }
    ]
  }
}

# ESTRUCTURA DE SALIDA (Agent1Output)

Cuando isComplete es true, el campo "output" DEBE seguir estrictamente este esquema JSON:

```json
{
  "buyerPersona": {
    "name": "Nombre creativo del perfil (ej: Carlos el CTO)",
    "narrative": "Narrativa detallada y humanizada de 3-4 párrafos describiendo al cliente ideal, sus dolores, motivaciones y contexto, redactada en tercera persona. Debe ser rica en detalles y 'humanizar' los datos recolectados.",
    "demographics": "Detalles demográficos concisos",
    "goals": ["Objetivo 1", "Objetivo 2"],
    "challenges": ["Desafío 1", "Desafío 2"]
  },
  "scalingUpTable": {
    "criteria": [
      {
        "name": "Nombre del Criterio (ej: Tamaño de Empresa)",
        "superGreen": "Descripción Super Green",
        "green": "Descripción Green",
        "yellow": "Descripción Yellow",
        "red": "Descripción Red",
        "notEligible": "Descripción Not Eligible"
      }
      // ... Repetir para todos los criterios identificados
    ]
  }
}
```

# RECORDATORIO CRÍTICO
Eres STATELESS. Recibirás el estado completo en cada turno.
"""

async def process_message(
    message: str,
    state: Dict[str, Any],
    account_context: Optional[Dict[str, Any]] = None,
    research_context: Optional[Dict[str, Any]] = None,
    ai_model: Optional[str] = None
) -> Dict[str, Any]:
    history = state.get("messages", [])
    
    if not history or history[0]["role"] != "system":
        full_prompt = SYSTEM_PROMPT
        if account_context:
            full_prompt += f"\n\nCONTEXTO DE CUENTA:\n- Consultor: {account_context.get('consultant_name')}\n- Empresa: {account_context.get('company_name')}\n- URL: {account_context.get('company_website')}"
        
        if research_context:
            full_prompt += f"\n\nINVESTIGACIÓN PREVIA ENCONTRADA (Úsala para confirmar en lugar de preguntar de cero):\n{json.dumps(research_context, indent=2)}"
        
        history = [{"role": "system", "content": full_prompt}] + [m for m in history if m["role"] != "system"]

    history.append({"role": "user", "content": message})

    try:
        response_text = await ai_provider_service.chat_completion(
            messages=history,
            temperature=0.7,
            model_override=ai_model
        )

        try:
            clean_text = response_text.strip()
            start_idx = clean_text.find('{')
            end_idx = clean_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                data = json.loads(clean_text[start_idx:end_idx+1])
                
                agent_msg = data.get("agentMessage") or data.get("message") or data.get("response") or data.get("text") or "No entendí bien, ¿podemos repetir?"
                updated_state = data.get("updatedState", {})
                updated_state["messages"] = history + [{"role": "assistant", "content": response_text}]
                
                progress_data = data.get("progress", 0)
                if isinstance(progress_data, dict):
                    progress_val = progress_data.get("percentage", 0)
                    progress_label = progress_data.get("label", f"{progress_val}%")
                    progress_step = progress_data.get("stepText", "")
                else:
                    try:
                        progress_val = int(progress_data)
                    except (ValueError, TypeError):
                        progress_val = 0
                    progress_label = f"[{updated_state.get('currentPhase', 'Level')}] {progress_val}%"
                    progress_step = f"Paso {updated_state.get('currentStep', 0)}"
                
                return {
                    "response": agent_msg,
                    "confidenceScore": data.get("confidenceScore", 50),
                    "buttons": data.get("buttons", []),
                    "state": updated_state,
                    "completed": data.get("isComplete", False),
                    "output": data.get("output"),
                    "progress": progress_val,
                    "progressLabel": progress_label,
                    "progressStep": progress_step
                }
            else:
                return {
                    "response": response_text,
                    "state": {"messages": history + [{"role": "assistant", "content": response_text}]},
                    "completed": False,
                    "output": None
                }
        except Exception:
             return {
                "response": response_text,
                "state": {"messages": history + [{"role": "assistant", "content": response_text}]},
                "completed": False,
                "output": None
            }

    except Exception as e:
        raise Exception(f"AI Agent Error: {str(e)}")

async def get_initial_message(
    account_context: Optional[Dict[str, Any]] = None,
    research_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    company = account_context.get("company_name", "tu cliente") if account_context else "tu cliente"
    consultant = account_context.get("consultant_name", "Consultor") if account_context else "Consultor"
    
    if research_context and any(research_context.values()):
        r = research_context
        industry = r.get('industria')
        desc = r.get('descripcion_corta')
        
        if industry:
            msg = f"Hola {consultant}, he estado investigando a **{company}** y veo que operan en el sector de **{industry}**. 🕵️‍♂️\n\n¿Es correcto o prefieres que ajustemos la industria antes de empezar a construir el Buyer Persona?"
            return {
                "message": msg,
                "buttons": ["Es correcto", "Es un poco diferente", "Editar industria"]
            }
        
        msg = f"Hola {consultant}, he estado investigando a **{company}**. Esto es lo que encontré:\n- **Descripción**: {desc or 'No disponible'}\n- **Público**: {r.get('publico_objetivo_estimado', 'No especificado')}\n\n¿Confirmas esta información?"
        return {
            "message": msg,
            "buttons": ["Confirmar e iniciar", "Necesito corregir algo"]
        }
    
    return {
        "message": f"Hola {consultant}, bienvenido a Booms Architect.\nVamos a crear el Buyer Persona para **{company}**. Como no encontré mucha información pública, ¿podrías contarme brevemente en qué industria o sector operan?",
        "buttons": ["SaaS B2B", "E-commerce", "Consultoría"]
    }
