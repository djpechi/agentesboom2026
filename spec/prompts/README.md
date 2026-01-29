# Prompts de Agentes - BOOMS Platform

## Estructura de Prompts

Cada agente tiene 2 componentes:

### 1. System Prompt
Define la personalidad, objetivo y formato de respuesta del agente.

### 2. Context Builder
Construye el contexto dinámico con:
- Outputs de agentes anteriores
- Estado actual de la conversación
- Datos del cliente

## Formato Esperado

Cada prompt debe seguir este formato para funcionalidad STATELESS:

```markdown
# Agente N: [Nombre]

## System Prompt

[Instrucciones base del agente]

## Response Format (JSON)

```json
{
  "agentMessage": "string - Siguiente pregunta o comentario del agente",
  "updatedState": {
    // Estado actualizado de la conversación
  },
  "progress": "number - 0 a 100",
  "isComplete": "boolean",
  "output": {
    // Solo cuando isComplete = true
    // Estructura específica del output de este agente
  }
}
```

## Context Template

[Cómo se construye el contexto con outputs anteriores]
```

## Archivos de Prompts

- `agent-1-booms.md` - Booms, the Buyer Persona Architect
- `agent-2-journey.md` - Arquitecto de Buyer's Journey
- `agent-3-offers.md` - Agente de Ofertas 100M
- `agent-4-channels.md` - Selector de Canales
- `agent-5-atlas.md` - Atlas, the AEO Strategist
- `agent-6-planner.md` - Planner, the Content Strategist
- `agent-7-budgets.md` - Agente de Budgets para Pauta

## Migración desde Relevance

Al pasar los prompts desde Relevance, considera:

1. **Variables de entrada**: Mapear las variables de Relevance a nuestro formato
2. **Contexto dinámico**: En BOOMS, el contexto se pasa en cada mensaje
3. **Formato de salida**: Debe ser JSON estructurado para parsing automático
4. **Preguntas secuenciales**: El agente debe hacer UNA pregunta a la vez
5. **Estado de completitud**: El agente debe saber cuándo ha terminado

## Próximo Paso

Pasa los prompts de Relevance en este formato:

```
AGENTE 1: BOOMS

[Pegar aquí el prompt completo de Relevance]

---

AGENTE 2: JOURNEY

[Pegar aquí el prompt completo de Relevance]

---

... etc
```

Los adaptaré al formato STATELESS de BOOMS.
