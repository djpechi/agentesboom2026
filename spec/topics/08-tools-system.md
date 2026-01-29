# Especificación: Sistema de Tools (Function Calling)

## Objetivo

Permitir que ciertos agentes usen herramientas externas durante la conversación, como búsqueda en Google, cálculos, o APIs externas.

## Tools Disponibles

### 1. Perplexity Search (RECOMENDADO)

**Agentes que lo usan**: Agente 2, 3, 4, 5, 7 (según necesidad)

**Descripción**: Buscar información actualizada usando Perplexity AI. Devuelve respuestas procesadas y resumidas, no solo links.

**Ventajas**:
- Respuestas ya resumidas y contextualizadas
- Incluye fuentes citadas
- Menos procesamiento requerido
- Mejor para agentes de IA

**Función**:
```typescript
interface PerplexitySearchTool {
  name: 'perplexity_search';
  description: 'Busca información actualizada y obtiene respuesta procesada';
  parameters: {
    query: string;      // Query de búsqueda
    searchDepth?: 'basic' | 'advanced'; // Profundidad (default: basic)
  };
}
```

**Implementación**:
```typescript
import fetch from 'node-fetch';

async function executePerplexitySearch(
  query: string,
  searchDepth: 'basic' | 'advanced' = 'basic'
): Promise<string> {
  const response = await fetch('https://api.perplexity.ai/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.PERPLEXITY_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: searchDepth === 'advanced' ? 'sonar-pro' : 'sonar',
      messages: [
        {
          role: 'system',
          content: 'Eres un asistente que proporciona información precisa y actualizada.'
        },
        {
          role: 'user',
          content: query
        }
      ],
      temperature: 0.2,
      max_tokens: 1000
    })
  });

  const data = await response.json();

  // Perplexity devuelve la respuesta procesada
  const answer = data.choices[0].message.content;
  const citations = data.citations || [];

  return JSON.stringify({
    answer,
    citations
  }, null, 2);
}
```

**Modelos Disponibles**:
- `sonar` - Búsqueda básica (más rápido, más barato)
- `sonar-pro` - Búsqueda avanzada (más profundo, más preciso)

### 2. Google Search (Alternativa)

**Si no quieres usar Perplexity**, puedes usar Google Search tradicional.

**Función**:
```typescript
interface GoogleSearchTool {
  name: 'google_search';
  description: 'Busca información actualizada en Google';
  parameters: {
    query: string;
    numResults?: number;
  };
}
```

**Implementación con SerpAPI** (más fácil):
```typescript
async function executeGoogleSearch(query: string): Promise<string> {
  const response = await fetch(
    `https://serpapi.com/search?q=${encodeURIComponent(query)}&api_key=${process.env.SERPAPI_KEY}`
  );

  const data = await response.json();

  const results = data.organic_results?.slice(0, 5).map(item => ({
    title: item.title,
    snippet: item.snippet,
    link: item.link
  })) || [];

  return JSON.stringify(results, null, 2);
}
```

**Alternativas de Google Search**:
- SerpAPI (más fácil, $50/mes por 5000 búsquedas)
- Google Custom Search API (100 búsquedas/día gratis)
- Brave Search API (gratis hasta 2000/mes)
- Tavily API (especializado para IA, gratis 1000/mes)

### 2. Calculator (Opcional)

Para cálculos complejos de presupuestos.

```typescript
interface CalculatorTool {
  name: 'calculator';
  description: 'Realiza cálculos matemáticos complejos';
  parameters: {
    expression: string;
  };
}
```

### 3. Web Scraper (Opcional)

Para obtener contenido específico de URLs.

```typescript
interface WebScraperTool {
  name: 'web_scraper';
  description: 'Obtiene contenido de una URL específica';
  parameters: {
    url: string;
  };
}
```

## Arquitectura con Function Calling

### OpenAI Function Calling (con Perplexity)

```typescript
import OpenAI from 'openai';

const tools: OpenAI.Chat.ChatCompletionTool[] = [
  {
    type: 'function',
    function: {
      name: 'perplexity_search',
      description: 'Busca información actualizada usando Perplexity AI. Devuelve respuestas procesadas y resumidas con fuentes.',
      parameters: {
        type: 'object',
        properties: {
          query: {
            type: 'string',
            description: 'Query de búsqueda en lenguaje natural'
          },
          searchDepth: {
            type: 'string',
            enum: ['basic', 'advanced'],
            description: 'Profundidad de búsqueda: basic (rápido) o advanced (más detallado)',
            default: 'basic'
          }
        },
        required: ['query']
      }
    }
  }
];

// En el chat
const completion = await openai.chat.completions.create({
  model: 'gpt-4o',
  messages: messages,
  tools: tools,
  tool_choice: 'auto'
});

// Verificar si el modelo quiere usar una tool
const responseMessage = completion.choices[0].message;

if (responseMessage.tool_calls) {
  // Ejecutar las tools solicitadas
  for (const toolCall of responseMessage.tool_calls) {
    if (toolCall.function.name === 'perplexity_search') {
      const args = JSON.parse(toolCall.function.arguments);
      const searchResults = await executePerplexitySearch(
        args.query,
        args.searchDepth || 'basic'
      );

      // Agregar resultado a los mensajes
      messages.push({
        role: 'tool',
        tool_call_id: toolCall.id,
        content: searchResults
      });
    }
  }

  // Llamar nuevamente al modelo con los resultados
  const secondResponse = await openai.chat.completions.create({
    model: 'gpt-4o',
    messages: messages
  });
}
```

### Anthropic Tool Use (con Perplexity)

```typescript
import Anthropic from '@anthropic-ai/sdk';

const tools: Anthropic.Tool[] = [
  {
    name: 'perplexity_search',
    description: 'Busca información actualizada usando Perplexity AI. Devuelve respuestas procesadas con fuentes.',
    input_schema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Query de búsqueda en lenguaje natural'
        },
        searchDepth: {
          type: 'string',
          enum: ['basic', 'advanced'],
          description: 'Profundidad de búsqueda',
          default: 'basic'
        }
      },
      required: ['query']
    }
  }
];

const response = await anthropic.messages.create({
  model: 'claude-opus-4-5-20251101',
  max_tokens: 4096,
  tools: tools,
  messages: messages
});

// Verificar tool use
if (response.stop_reason === 'tool_use') {
  const toolUse = response.content.find(block => block.type === 'tool_use');

  if (toolUse && toolUse.name === 'perplexity_search') {
    const searchResults = await executePerplexitySearch(
      toolUse.input.query,
      toolUse.input.searchDepth || 'basic'
    );

    // Continuar conversación con resultados
    messages.push({
      role: 'assistant',
      content: response.content
    });

    messages.push({
      role: 'user',
      content: [
        {
          type: 'tool_result',
          tool_use_id: toolUse.id,
          content: searchResults
        }
      ]
    });
  }
}
```

### Google Gemini Function Calling (con Perplexity)

```typescript
import { GoogleGenerativeAI } from '@google/generative-ai';

const tools = [
  {
    functionDeclarations: [
      {
        name: 'perplexity_search',
        description: 'Busca información actualizada usando Perplexity AI. Devuelve respuestas procesadas.',
        parameters: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Query de búsqueda en lenguaje natural'
            },
            searchDepth: {
              type: 'string',
              enum: ['basic', 'advanced'],
              description: 'Profundidad de búsqueda'
            }
          },
          required: ['query']
        }
      }
    ]
  }
];

const model = genAI.getGenerativeModel({
  model: 'gemini-2.0-flash-exp',
  tools: tools
});

const result = await model.generateContent({
  contents: [{ role: 'user', parts: [{ text: userMessage }] }]
});

// Verificar function call
const functionCall = result.response.functionCall();
if (functionCall && functionCall.name === 'perplexity_search') {
  const searchResults = await executePerplexitySearch(
    functionCall.args.query,
    functionCall.args.searchDepth || 'basic'
  );

  // Enviar resultados de vuelta
  const result2 = await model.generateContent({
    contents: [
      { role: 'user', parts: [{ text: userMessage }] },
      { role: 'model', parts: [{ functionCall: functionCall }] },
      { role: 'function', parts: [{ functionResponse: {
        name: 'perplexity_search',
        response: searchResults
      } }] }
    ]
  });
}
```

## Actualización del AIProviderService

```typescript
interface AIRequest {
  model: string;
  messages: AIMessage[];
  responseFormat?: 'json' | 'text';
  temperature?: number;
  maxTokens?: number;
  tools?: Tool[]; // NUEVO
}

interface Tool {
  name: string;
  description: string;
  parameters: Record<string, any>;
  executor: (args: any) => Promise<string>; // Función que ejecuta la tool
}

interface AIResponse {
  content: string;
  model: string;
  usage?: TokenUsage;
  provider: string;
  toolCalls?: ToolCall[]; // NUEVO - Si el modelo quiere usar tools
}

interface ToolCall {
  id: string;
  name: string;
  arguments: any;
}
```

## Configuración por Agente

```typescript
// /backend/config/agentTools.ts

export const AGENT_TOOLS = {
  1: [], // Booms - No usa tools
  2: [], // Journey - No usa tools
  3: ['google_search'], // Ofertas - Busca ejemplos de ofertas exitosas
  4: ['google_search'], // Canales - Busca tendencias de marketing
  5: ['google_search'], // Atlas - Busca tendencias SEO/AEO
  6: [], // Planner - No usa tools
  7: ['google_search'] // Budgets - Busca costos de advertising actualizados
};

export function getToolsForAgent(stageNumber: number): Tool[] {
  const toolNames = AGENT_TOOLS[stageNumber] || [];

  return toolNames.map(name => {
    switch (name) {
      case 'google_search':
        return {
          name: 'google_search',
          description: 'Busca información actualizada en Google',
          parameters: {
            type: 'object',
            properties: {
              query: { type: 'string', description: 'Query de búsqueda' }
            },
            required: ['query']
          },
          executor: executeGoogleSearch
        };
      default:
        throw new Error(`Tool desconocida: ${name}`);
    }
  });
}
```

## Flujo con Tools

```typescript
async function chatWithAgent(req, res) {
  const { stageNumber, userMessage, conversationState } = req.body;

  // Obtener tools para este agente
  const tools = getToolsForAgent(stageNumber);

  let messages = buildMessages(stageNumber, userMessage, conversationState);
  let maxIterations = 5; // Prevenir loops infinitos
  let iterations = 0;

  while (iterations < maxIterations) {
    const aiResponse = await aiProvider.chat({
      model: aiModel,
      messages: messages,
      tools: tools.map(t => ({
        name: t.name,
        description: t.description,
        parameters: t.parameters
      })),
      responseFormat: 'json'
    });

    // Si no hay tool calls, retornar respuesta
    if (!aiResponse.toolCalls || aiResponse.toolCalls.length === 0) {
      return res.json(JSON.parse(aiResponse.content));
    }

    // Ejecutar tool calls
    for (const toolCall of aiResponse.toolCalls) {
      const tool = tools.find(t => t.name === toolCall.name);
      if (tool) {
        const result = await tool.executor(toolCall.arguments);

        // Agregar resultado a mensajes
        messages.push({
          role: 'tool',
          name: toolCall.name,
          content: result
        });
      }
    }

    iterations++;
  }

  // Si llegamos aquí, hubo demasiadas iteraciones
  res.status(500).json({ error: 'Demasiadas llamadas a tools' });
}
```

## Variables de Entorno

```env
# Perplexity (RECOMENDADO)
PERPLEXITY_API_KEY=pplx-...

# Alternativa: SerpAPI (Google Search wrapper)
SERPAPI_KEY=...

# Alternativa: Google Custom Search
GOOGLE_SEARCH_API_KEY=AIza...
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id

# Alternativa: Brave Search
BRAVE_SEARCH_API_KEY=...

# Alternativa: Tavily
TAVILY_API_KEY=...
```

## Base de Datos: Logging de Tool Calls

Opcional: guardar qué tools se usaron para analytics.

```sql
CREATE TABLE tool_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  stage_id UUID NOT NULL REFERENCES stages(id) ON DELETE CASCADE,
  tool_name VARCHAR(100) NOT NULL,
  arguments JSONB NOT NULL,
  result TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tool_usage_stage_id ON tool_usage(stage_id);
CREATE INDEX idx_tool_usage_tool_name ON tool_usage(tool_name);
```

## Testing

```typescript
describe('Tools System', () => {
  it('debe ejecutar google_search correctamente', async () => {
    const result = await executeGoogleSearch('mejores ofertas 100M');
    expect(result).toContain('title');
    expect(result).toContain('snippet');
  });

  it('agente debe usar tool cuando sea necesario', async () => {
    const response = await chatWithAgent({
      stageNumber: 3,
      userMessage: 'Busca ejemplos de ofertas exitosas en SaaS',
      conversationState: {}
    });

    // Verificar que se usó la tool
    const toolUsage = await db.query(
      'SELECT * FROM tool_usage WHERE tool_name = $1',
      ['google_search']
    );

    expect(toolUsage.rows.length).toBeGreaterThan(0);
  });
});
```

## Costos

### Perplexity (RECOMENDADO)

**Modelos**:
- `sonar` (básico): $0.001 por request (~1000 requests = $1)
- `sonar-pro` (avanzado): $0.005 por request (~1000 requests = $5)

**Ventajas**:
- Respuestas ya procesadas (ahorra tokens de IA)
- Incluye fuentes citadas
- Mejor para agentes de IA
- Sin límite de búsquedas (solo pagas por request)

**Plan**:
- Pay-as-you-go (sin mínimo mensual)
- $5 de crédito inicial gratis

### Alternativas

**SerpAPI** (Google Search wrapper):
- Gratis: 100 búsquedas/mes
- De pago: desde $50/mes (5000 búsquedas)

**Google Custom Search**:
- Gratis: 100 búsquedas/día
- De pago: $5 por 1000 búsquedas

**Brave Search**:
- Gratis: 2000 búsquedas/mes
- De pago: $0.50 por 1000 búsquedas

**Tavily** (optimizado para IA):
- Gratis: 1000 búsquedas/mes
- De pago: $0.002 por búsqueda

### Comparación de Costos

| Provider | Costo por 1000 búsquedas | Respuestas procesadas | API para IA |
|----------|--------------------------|----------------------|-------------|
| Perplexity (sonar) | $1 | ✅ Sí | ✅ Sí |
| Perplexity (sonar-pro) | $5 | ✅ Sí | ✅ Sí |
| Tavily | $2 | ✅ Sí | ✅ Sí |
| SerpAPI | $10 | ❌ No (solo links) | ❌ No |
| Google Custom Search | $5 | ❌ No (solo links) | ❌ No |

**Recomendación**:
1. **MVP/Desarrollo**: Perplexity `sonar` (más barato, suficientemente bueno)
2. **Producción**: Perplexity `sonar-pro` (mejor calidad de respuestas)
3. **Alternativa gratis**: Tavily (1000 búsquedas/mes gratis)
