# Especificación: AI Provider Service

## Objetivo

Crear un servicio unificado que abstrae 3 proveedores de IA (OpenAI, Anthropic, Google) permitiendo usar cualquiera con la misma interfaz y normalización de respuestas.

## Modelos Disponibles

| Provider | Modelo | Identificador | Default |
|----------|--------|---------------|---------|
| OpenAI | GPT-4o | `openai-gpt4o` | ✅ |
| Anthropic | Claude Opus 4 | `anthropic-claude-opus-4` | |
| Google | Gemini 2.5 Pro | `google-gemini-2.5-pro` | |

## Variables de Entorno

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Google AI
GOOGLE_AI_API_KEY=AIza...

# Default model
DEFAULT_AI_MODEL=openai-gpt4o
```

## Arquitectura del Servicio

### Ubicación
`/backend/services/aiProvider.ts`

### Estructura

```typescript
// Tipos compartidos
interface AIMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface AIRequest {
  model: string; // 'openai-gpt4o' | 'anthropic-claude-opus-4' | 'google-gemini-2.5-pro'
  messages: AIMessage[];
  responseFormat?: 'json' | 'text';
  temperature?: number;
  maxTokens?: number;
}

interface AIResponse {
  content: string; // JSON string si responseFormat='json'
  model: string;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  provider: 'openai' | 'anthropic' | 'google';
}

// Servicio principal
class AIProviderService {
  async chat(request: AIRequest): Promise<AIResponse>;
  private chatWithOpenAI(request: AIRequest): Promise<AIResponse>;
  private chatWithAnthropic(request: AIRequest): Promise<AIResponse>;
  private chatWithGoogle(request: AIRequest): Promise<AIResponse>;
}
```

## Implementación de Referencia

### Servicio Principal

```typescript
import OpenAI from 'openai';
import Anthropic from '@anthropic-ai/sdk';
import { GoogleGenerativeAI } from '@google/generative-ai';

class AIProviderService {
  private openai: OpenAI;
  private anthropic: Anthropic;
  private google: GoogleGenerativeAI;

  constructor() {
    this.openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
    this.anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
    this.google = new GoogleGenerativeAI(process.env.GOOGLE_AI_API_KEY);
  }

  async chat(request: AIRequest): Promise<AIResponse> {
    const { model } = request;

    if (model.startsWith('openai-')) {
      return this.chatWithOpenAI(request);
    } else if (model.startsWith('anthropic-')) {
      return this.chatWithAnthropic(request);
    } else if (model.startsWith('google-')) {
      return this.chatWithGoogle(request);
    } else {
      throw new Error(`Modelo no soportado: ${model}`);
    }
  }

  private async chatWithOpenAI(request: AIRequest): Promise<AIResponse> {
    const completion = await this.openai.chat.completions.create({
      model: 'gpt-4o',
      messages: request.messages,
      response_format: request.responseFormat === 'json'
        ? { type: 'json_object' }
        : undefined,
      temperature: request.temperature ?? 0.7,
      max_tokens: request.maxTokens
    });

    return {
      content: completion.choices[0].message.content || '',
      model: request.model,
      usage: {
        promptTokens: completion.usage?.prompt_tokens || 0,
        completionTokens: completion.usage?.completion_tokens || 0,
        totalTokens: completion.usage?.total_tokens || 0
      },
      provider: 'openai'
    };
  }

  private async chatWithAnthropic(request: AIRequest): Promise<AIResponse> {
    // Separar mensajes de sistema de los demás
    const systemMessages = request.messages.filter(m => m.role === 'system');
    const otherMessages = request.messages.filter(m => m.role !== 'system');

    const systemPrompt = systemMessages.map(m => m.content).join('\n\n');

    const response = await this.anthropic.messages.create({
      model: 'claude-opus-4-5-20251101',
      max_tokens: request.maxTokens ?? 4096,
      system: systemPrompt,
      messages: otherMessages.map(m => ({
        role: m.role as 'user' | 'assistant',
        content: m.content
      })),
      temperature: request.temperature ?? 0.7
    });

    // Si se pidió JSON, extraer del markdown si está presente
    let content = response.content[0].type === 'text'
      ? response.content[0].text
      : '';

    if (request.responseFormat === 'json') {
      // Antropic puede envolver JSON en markdown, extraerlo
      const jsonMatch = content.match(/```json\s*([\s\S]*?)\s*```/);
      if (jsonMatch) {
        content = jsonMatch[1];
      }
    }

    return {
      content,
      model: request.model,
      usage: {
        promptTokens: response.usage.input_tokens,
        completionTokens: response.usage.output_tokens,
        totalTokens: response.usage.input_tokens + response.usage.output_tokens
      },
      provider: 'anthropic'
    };
  }

  private async chatWithGoogle(request: AIRequest): Promise<AIResponse> {
    const model = this.google.getGenerativeModel({
      model: 'gemini-2.0-flash-exp',
      generationConfig: {
        temperature: request.temperature ?? 0.7,
        maxOutputTokens: request.maxTokens,
        responseMimeType: request.responseFormat === 'json'
          ? 'application/json'
          : 'text/plain'
      }
    });

    // Convertir mensajes al formato de Gemini
    const systemMessages = request.messages.filter(m => m.role === 'system');
    const userMessages = request.messages.filter(m => m.role === 'user');
    const assistantMessages = request.messages.filter(m => m.role === 'assistant');

    // Gemini maneja system instructions separadamente
    const systemInstruction = systemMessages.map(m => m.content).join('\n\n');

    // Construir historial de chat
    const history = [];
    for (let i = 0; i < Math.max(userMessages.length, assistantMessages.length); i++) {
      if (userMessages[i]) {
        history.push({
          role: 'user',
          parts: [{ text: userMessages[i].content }]
        });
      }
      if (assistantMessages[i]) {
        history.push({
          role: 'model',
          parts: [{ text: assistantMessages[i].content }]
        });
      }
    }

    const chat = model.startChat({
      history,
      systemInstruction
    });

    // El último mensaje del usuario
    const lastUserMessage = userMessages[userMessages.length - 1]?.content || '';
    const result = await chat.sendMessage(lastUserMessage);
    const response = result.response;

    return {
      content: response.text(),
      model: request.model,
      usage: {
        promptTokens: response.usageMetadata?.promptTokenCount || 0,
        completionTokens: response.usageMetadata?.candidatesTokenCount || 0,
        totalTokens: response.usageMetadata?.totalTokenCount || 0
      },
      provider: 'google'
    };
  }
}

export const aiProvider = new AIProviderService();
```

## Uso en Endpoints

### Actualizar endpoint de chat

```typescript
// /backend/routes/agents.ts
import { aiProvider } from '../services/aiProvider';

async function chatWithAgent(req, res) {
  const {
    accountId,
    stageNumber,
    userMessage,
    conversationState,
    previousOutputs
  } = req.body;

  // Obtener modelo seleccionado de la cuenta
  const account = await db.query(
    'SELECT ai_model FROM accounts WHERE id = $1',
    [accountId]
  );
  const aiModel = account.rows[0]?.ai_model || process.env.DEFAULT_AI_MODEL;

  // Construir mensajes
  const systemPrompt = getAgentSystemPrompt(stageNumber);
  const contextPrompt = buildContextPrompt(previousOutputs, conversationState);

  const messages: AIMessage[] = [
    { role: 'system', content: systemPrompt },
    { role: 'system', content: contextPrompt },
    { role: 'user', content: userMessage }
  ];

  try {
    // Llamar al servicio unificado
    const aiResponse = await aiProvider.chat({
      model: aiModel,
      messages,
      responseFormat: 'json',
      temperature: 0.7
    });

    const response = JSON.parse(aiResponse.content);

    // Guardar qué modelo se usó
    await db.query(
      'UPDATE stages SET ai_model_used = $1 WHERE id = $2',
      [aiModel, stageId]
    );

    // Guardar mensajes en historial
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
  } catch (error) {
    console.error('Error en AI Provider:', error);
    res.status(500).json({
      error: 'Error al procesar con el modelo de IA',
      details: error.message
    });
  }
}
```

## Endpoints de Configuración

### GET /api/accounts/:accountId/ai-model

Obtener modelo configurado para una cuenta.

```typescript
async function getAccountAIModel(req, res) {
  const { accountId } = req.params;

  const result = await db.query(
    'SELECT ai_model FROM accounts WHERE id = $1',
    [accountId]
  );

  res.json({ aiModel: result.rows[0]?.ai_model || 'openai-gpt4o' });
}
```

### PUT /api/accounts/:accountId/ai-model

Cambiar modelo de IA para una cuenta.

```typescript
async function updateAccountAIModel(req, res) {
  const { accountId } = req.params;
  const { aiModel } = req.body;

  const validModels = [
    'openai-gpt4o',
    'anthropic-claude-opus-4',
    'google-gemini-2.5-pro'
  ];

  if (!validModels.includes(aiModel)) {
    return res.status(400).json({ error: 'Modelo no válido' });
  }

  await db.query(
    'UPDATE accounts SET ai_model = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2',
    [aiModel, accountId]
  );

  res.json({ success: true, aiModel });
}
```

## Frontend: Selector de Modelo

### Component: AIModelSelector

```typescript
// /frontend/components/AIModelSelector.tsx
import { Select } from '@/components/ui/select';

interface AIModel {
  id: string;
  name: string;
  provider: string;
  description: string;
}

const models: AIModel[] = [
  {
    id: 'openai-gpt4o',
    name: 'GPT-4o',
    provider: 'OpenAI',
    description: 'Rápido y versátil - Default'
  },
  {
    id: 'anthropic-claude-opus-4',
    name: 'Claude Opus 4',
    provider: 'Anthropic',
    description: 'Razonamiento avanzado y profundo'
  },
  {
    id: 'google-gemini-2.5-pro',
    name: 'Gemini 2.5 Pro',
    provider: 'Google',
    description: 'Multimodal y contexto largo'
  }
];

export function AIModelSelector({ accountId, currentModel, onChange }) {
  return (
    <Select value={currentModel} onValueChange={onChange}>
      {models.map(model => (
        <SelectItem key={model.id} value={model.id}>
          <div>
            <div className="font-medium">{model.name}</div>
            <div className="text-sm text-gray-500">{model.description}</div>
          </div>
        </SelectItem>
      ))}
    </Select>
  );
}
```

### Integración en Account Settings

Mostrar selector en la configuración de cuenta o al iniciar una sesión de agente.

```typescript
// En AccountSettings.tsx
const [aiModel, setAIModel] = useState('openai-gpt4o');

const handleModelChange = async (newModel: string) => {
  await api.put(`/api/accounts/${accountId}/ai-model`, { aiModel: newModel });
  setAIModel(newModel);
  toast.success('Modelo actualizado');
};

<AIModelSelector
  accountId={accountId}
  currentModel={aiModel}
  onChange={handleModelChange}
/>
```

## Manejo de Errores

Cada provider puede tener errores específicos. Normalizar en el servicio:

```typescript
try {
  // llamada al provider
} catch (error) {
  if (error.status === 429) {
    throw new Error('Límite de tasa excedido. Intenta en unos minutos.');
  } else if (error.status === 401) {
    throw new Error('API key inválida o expirada.');
  } else if (error.status === 500) {
    throw new Error('Error del proveedor de IA. Intenta otro modelo.');
  } else {
    throw new Error(`Error del modelo de IA: ${error.message}`);
  }
}
```

## Testing

Crear mocks para cada provider en tests:

```typescript
// /backend/services/__tests__/aiProvider.test.ts
describe('AIProviderService', () => {
  it('debe normalizar respuestas de OpenAI', async () => {
    // mock de OpenAI
  });

  it('debe normalizar respuestas de Anthropic', async () => {
    // mock de Anthropic
  });

  it('debe normalizar respuestas de Google', async () => {
    // mock de Google
  });

  it('debe manejar errores de providers', async () => {
    // test de error handling
  });
});
```

## Costos y Analytics

Guardar información de uso para tracking de costos:

```typescript
// Agregar a conversation_history.metadata
{
  "modelUsed": "anthropic-claude-opus-4",
  "provider": "anthropic",
  "usage": {
    "promptTokens": 1234,
    "completionTokens": 567,
    "totalTokens": 1801
  }
}
```

Query para analizar costos:

```sql
SELECT
  ai_model_used,
  COUNT(*) as sessions,
  AVG(CAST(output->>'totalTokens' AS INTEGER)) as avg_tokens
FROM stages
WHERE ai_model_used IS NOT NULL
GROUP BY ai_model_used;
```
