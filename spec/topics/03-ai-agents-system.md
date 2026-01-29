# Especificación: Sistema de Agentes de IA

## Tecnología

- **Proveedores**: OpenAI GPT-4o (default), Anthropic Claude Opus 4, Google Gemini 2.5 Pro
- **Arquitectura**: STATELESS
- **Bibliotecas**: openai, @anthropic-ai/sdk, @google/generative-ai
- **Servicio**: AIProviderService (abstracción unificada)

## Selección de Modelo de IA

Los usuarios pueden elegir qué modelo de IA usar:

- **A nivel de cuenta**: Configuración en settings de la cuenta (afecta todas las nuevas sesiones)
- **Persistencia**: El modelo usado se guarda en `stages.ai_model_used` para referencia

### Modelos Disponibles

| Modelo | Identificador | Provider | Características |
|--------|--------------|----------|-----------------|
| GPT-4o | `openai-gpt4o` | OpenAI | Rápido, versátil (default) |
| Claude Opus 4 | `anthropic-claude-opus-4` | Anthropic | Razonamiento profundo |
| Gemini 2.5 Pro | `google-gemini-2.5-pro` | Google | Multimodal, contexto largo |

**Ver especificación completa**: `spec/topics/04-ai-provider-service.md`

## Principio STATELESS

**CRÍTICO**: Los agentes NO tienen memoria entre mensajes. Cada request es independiente.

### Flujo de Request

```javascript
// Cada mensaje incluye TODO el contexto
{
  accountId: "uuid",
  stageNumber: 1,
  previousOutputs: {
    // Outputs de etapas anteriores (si existen)
    stage1: { buyerPersona: {...}, scalingUpTable: [...] },
    stage2: { buyersJourney: [...] }
  },
  conversationState: {
    // Estado actual de la conversación
    currentQuestion: 3,
    collectedData: { industry: "SaaS B2B" }
  },
  userMessage: "Vendemos software de gestión de proyectos"
}
```

### Flujo de Response

```javascript
{
  agentMessage: "Excelente. ¿Cuál es el tamaño típico de empresas que compran?",
  updatedState: {
    currentQuestion: 4,
    collectedData: {
      industry: "SaaS B2B",
      product: "Software de gestión de proyectos"
    }
  },
  progress: 40, // Porcentaje de completitud
  isComplete: false,
  output: null // Solo se llena cuando isComplete = true
}
```

## Definición de los 7 Agentes

### Agente 1: Booms, the Buyer Persona Architect

**Objetivo**: Construir buyer persona detallado y tabla Scaling Up.

**Input**: Cuestionario conversacional (nada previo).

**Preguntas Clave**:
1. ¿Qué producto/servicio ofrece tu cliente?
2. ¿Quién es el decision maker en la compra?
3. ¿Qué problema específico resuelves?
4. ¿Cuál es el perfil demográfico del comprador?
5. ¿Cuáles son sus pain points principales?
6. ¿Qué objeciones típicas tienen?
7. ¿Qué los motiva a comprar?

**Output Esperado**:
```json
{
  "buyerPersona": {
    "name": "Carlos el CTO",
    "age": 38,
    "role": "Chief Technology Officer",
    "company": "Empresa SaaS 50-200 empleados",
    "goals": ["Escalar equipo técnico", "Mejorar productividad"],
    "painPoints": ["Falta de visibilidad", "Herramientas fragmentadas"],
    "motivations": ["ROI medible", "Fácil adopción"],
    "objections": ["Costo", "Curva de aprendizaje"],
    "narrative": "Carlos es un CTO de 38 años..."
  },
  "scalingUpTable": [
    { "category": "Identificadores", "data": "CTO, 35-45 años" },
    { "category": "Objetivos", "data": "Escalar equipo" }
  ]
}
```

### Agente 2: Arquitecto de Buyer's Journey

**Objetivo**: Mapear el journey completo en 15 columnas.

**Input**: Buyer Persona del Agente 1.

**Output Esperado**:
```json
{
  "buyersJourney": [
    {
      "stage": "Awareness",
      "trigger": "Equipo desorganizado",
      "thoughtProcess": "¿Por qué estamos tan ineficientes?",
      "emotions": "Frustración",
      "questions": "¿Existen herramientas mejores?",
      "contentNeeds": "Blog posts sobre señales de desorganización",
      "channels": "Google, LinkedIn",
      "... (15 columnas total)"
    },
    {
      "stage": "Consideration",
      "... (mismo formato)"
    },
    {
      "stage": "Decision",
      "... (mismo formato)"
    }
  ]
}
```

### Agente 3: Agente de Ofertas 100M

**Objetivo**: Crear oferta irresistible usando fórmula Hormozi + StoryBrand.

**Input**: Buyer Persona + Journey.

**Output Esperado**:
```json
{
  "offer": {
    "headline": "Gestión de Proyectos que Tu Equipo Usará (Sin Capacitación)",
    "valueProposition": "...",
    "hormozi": {
      "dreamOutcome": "Productividad 2x en 30 días",
      "perceivedLikelihood": "94% de adopción promedio",
      "timeDelay": "Implementación en 1 semana",
      "effortSacrifice": "Cero capacitación necesaria"
    },
    "storyBrand": {
      "character": "CTOs de empresas SaaS",
      "problem": "Herramientas complejas que nadie usa",
      "guide": "Nosotros",
      "plan": "1. Onboarding automático, 2. Soporte 24/7",
      "callToAction": "Demo personalizada en 15 min",
      "success": "Equipos 2x más productivos",
      "failure": "Seguir perdiendo tiempo en reuniones"
    },
    "guarantee": "30 días gratis, sin tarjeta de crédito"
  }
}
```

### Agente 4: Selector de Canales

**Objetivo**: Priorizar canales de marketing con scoring.

**Input**: Todo lo anterior.

**Output Esperado**:
```json
{
  "channels": [
    {
      "name": "LinkedIn Ads",
      "score": 9.2,
      "rationale": "Alto nivel de decision makers",
      "budget": 3000,
      "expectedROI": "4.5x",
      "priority": "Alta"
    },
    {
      "name": "Google Search",
      "score": 8.5,
      "... (similar)"
    }
  ]
}
```

### Agente 5: Atlas, the AEO Strategist

**Objetivo**: Pilares de contenido + Clusters SEO/AEO.

**Input**: Todo lo anterior.

**Output Esperado**:
```json
{
  "contentPillars": [
    {
      "pillar": "Productividad de Equipos Remotos",
      "subTopics": ["Herramientas", "Cultura", "Métricas"],
      "keywords": ["gestión equipos remotos", "productividad remote"],
      "searchIntent": "Informacional"
    }
  ],
  "seoClusters": [
    {
      "pillarPage": "Guía Completa de Gestión de Proyectos",
      "clusterPages": ["Metodologías Ágiles", "Scrum vs Kanban"]
    }
  ]
}
```

### Agente 6: Planner, the Content Strategist

**Objetivo**: Calendario editorial 90 días.

**Input**: Todo lo anterior.

**Output Esperado**:
```json
{
  "calendar": [
    {
      "week": 1,
      "contentPieces": [
        {
          "title": "5 Señales de que Tu Equipo Necesita Nueva Herramienta",
          "format": "Blog Post",
          "channel": "Blog + LinkedIn",
          "buyerStage": "Awareness",
          "publishDate": "2024-01-08"
        }
      ]
    }
  ]
}
```

### Agente 7: Agente de Budgets para Pauta

**Objetivo**: Plan de medios + presupuesto por canal.

**Input**: Todo lo anterior.

**Output Esperado**:
```json
{
  "mediaPlan": {
    "totalBudget": 10000,
    "duration": "90 días",
    "breakdown": [
      {
        "channel": "LinkedIn Ads",
        "budget": 3000,
        "allocation": "30%",
        "kpis": {
          "impressions": 150000,
          "clicks": 3000,
          "leads": 90,
          "cpl": 33.33
        }
      }
    ]
  }
}
```

## Implementación Backend

### Endpoint Principal

```javascript
POST /api/agents/chat
```

**Request**:
```json
{
  "accountId": "uuid",
  "stageNumber": 1,
  "userMessage": "Vendemos software B2B",
  "conversationState": {...},
  "previousOutputs": {...}
}
```

**Response**:
```json
{
  "agentMessage": "Perfecto...",
  "updatedState": {...},
  "progress": 30,
  "isComplete": false,
  "output": null
}
```

### Código de Referencia

```javascript
import { aiProvider } from '../services/aiProvider';

async function chatWithAgent(req, res) {
  const {
    accountId,
    stageNumber,
    userMessage,
    conversationState,
    previousOutputs
  } = req.body;

  // Obtener modelo configurado de la cuenta
  const account = await db.query(
    'SELECT ai_model FROM accounts WHERE id = $1',
    [accountId]
  );
  const aiModel = account.rows[0]?.ai_model || process.env.DEFAULT_AI_MODEL;

  // Construir prompt con TODO el contexto
  const systemPrompt = getAgentSystemPrompt(stageNumber);
  const contextPrompt = buildContextPrompt(previousOutputs, conversationState);

  // Llamar al servicio unificado de IA
  const aiResponse = await aiProvider.chat({
    model: aiModel,
    messages: [
      { role: "system", content: systemPrompt },
      { role: "system", content: contextPrompt },
      { role: "user", content: userMessage }
    ],
    responseFormat: 'json',
    temperature: 0.7
  });

  const response = JSON.parse(aiResponse.content);

  // Guardar qué modelo se usó
  await db.query(
    'UPDATE stages SET ai_model_used = $1 WHERE id = $2',
    [aiModel, stageId]
  );

  // Guardar en BD
  await saveConversationMessage(stageId, 'user', userMessage);
  await saveConversationMessage(stageId, 'assistant', response.agentMessage);

  if (response.isComplete) {
    await updateStageOutput(stageId, response.output);
    await completeStage(stageId);
  }

  res.json({
    ...response,
    metadata: {
      modelUsed: aiModel,
      provider: aiResponse.provider,
      usage: aiResponse.usage
    }
  });
}
```

### System Prompts

Cada agente tiene un system prompt específico en:
`/backend/prompts/agent-{N}-system.txt`

Ejemplo (Agente 1):
```
Eres Booms, the Buyer Persona Architect. Tu trabajo es guiar una conversación para construir un buyer persona detallado.

INSTRUCCIONES:
- Haz preguntas conversacionales, una a la vez
- Profundiza en pain points y motivaciones
- Al final, genera JSON con buyerPersona y scalingUpTable
- Responde SIEMPRE en formato JSON con estructura:
  {
    "agentMessage": "tu pregunta o comentario",
    "updatedState": { estado actualizado },
    "progress": número 0-100,
    "isComplete": boolean,
    "output": objeto con buyerPersona y scalingUpTable (solo si isComplete=true)
  }
```

## Variables de Entorno

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Google AI
GOOGLE_AI_API_KEY=AIza...

# Default Model
DEFAULT_AI_MODEL=openai-gpt4o
```

## Manejo de Errores

- Timeout: 30 segundos
- Retry: 2 intentos
- Fallback: Mensaje de error amigable al usuario
