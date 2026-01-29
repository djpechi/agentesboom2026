# JTBD: Interactuar con Agentes de IA

## Contexto

Como **consultor de marketing**, necesito que cada agente de IA me guíe conversacionalmente para generar el entregable correspondiente de esa etapa.

## Job Statement

**Cuando** accedo a una etapa del pipeline,
**Quiero** tener una conversación guiada con el agente de IA,
**Para** que genere el entregable específico de esa etapa basándose en mis respuestas y el contexto de etapas anteriores.

## Situación Actual (Pain Points)

- Crear documentos estratégicos desde cero es tedioso
- No siempre sé qué preguntas hacer al cliente
- La calidad varía según mi experiencia
- No aprovecho outputs de etapas anteriores

## Resultado Deseado (Gains)

- Conversación estructurada con cada agente
- El agente me hace las preguntas correctas
- Usa automáticamente contexto de etapas anteriores
- Genera output profesional al finalizar
- Proceso fluido y natural

## Criterios de Éxito

- ✅ Cada agente tiene personalidad/enfoque específico
- ✅ El agente me hace preguntas conversacionales
- ✅ Puedo responder en lenguaje natural
- ✅ El agente usa outputs de etapas anteriores como contexto
- ✅ Veo progreso de la conversación
- ✅ Puedo revisar y editar mis respuestas
- ✅ Al completar, el agente genera el entregable estructurado
- ✅ Puedo marcar la etapa como completada

## Arquitectura STATELESS (Requisito Crítico)

Cada agente NO tiene memoria. En cada mensaje:

```
REQUEST:
{
  "accountId": "123",
  "stage": 1,
  "previousOutputs": [/* outputs de etapas anteriores */],
  "currentState": {/* estado actual de la conversación */},
  "userMessage": "Mi cliente vende software B2B"
}

RESPONSE:
{
  "agentMessage": "Perfecto. ¿Cuál es el tamaño típico de las empresas que compran?",
  "updatedState": {/* nuevo estado */},
  "progress": 30,
  "isComplete": false
}
```

## Flujo del Usuario

1. Click en etapa disponible del pipeline
2. Ver interfaz de chat con el agente
3. Leer mensaje inicial del agente
4. Responder preguntas del agente
5. Ver cómo el agente procesa y hace siguiente pregunta
6. Continuar conversación hasta completar
7. Ver output generado
8. Revisar output
9. Marcar como completada (o editar)
10. Regresar al pipeline

## Dependencias

- Integración con OpenAI GPT-4o
- Sistema de prompts para cada agente
- Gestión de estado conversacional
- Almacenamiento de outputs
- UI de chat responsiva
- Sistema de validación de completitud
