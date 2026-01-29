# Especificación: Paso Automático de Contexto de Cuenta

## Objetivo

Pasar automáticamente información de la cuenta (consultor, empresa, website) a todos los agentes, eliminando la necesidad de preguntar por datos que ya existen.

## Datos Disponibles por Defecto

Cuando un agente inicia conversación, tiene acceso automático a:

### Desde `users` table:
- **Nombre del consultor**: `users.full_name`

### Desde `accounts` table:
- **Nombre de la empresa cliente**: `accounts.client_name`
- **Sitio web de la empresa**: `accounts.company_website`
- **Modelo de IA seleccionado**: `accounts.ai_model`

## Actualización del Schema de BD

```sql
-- Agregar company_website a accounts si no existe
ALTER TABLE accounts
ADD COLUMN IF NOT EXISTS company_website VARCHAR(500);
```

## Implementación en Backend

### 1. Endpoint de Chat Actualizado

```typescript
// /backend/routes/agents.ts

async function chatWithAgent(req: Request, res: Response) {
  const {
    accountId,
    stageNumber,
    userMessage,
    conversationState,
    previousOutputs
  } = req.body;

  const { userId } = req.user; // Del middleware de autenticación

  // Obtener información de cuenta Y usuario
  const accountData = await db.query(
    `SELECT
      a.id,
      a.client_name,
      a.company_website,
      a.ai_model,
      u.full_name as consultant_name
     FROM accounts a
     JOIN users u ON a.user_id = u.id
     WHERE a.id = $1 AND a.user_id = $2`,
    [accountId, userId]
  );

  if (accountData.rows.length === 0) {
    return res.status(404).json({ error: 'Cuenta no encontrada' });
  }

  const account = accountData.rows[0];

  // Construir contexto automático
  const accountContext = {
    consultantName: account.consultant_name,
    companyName: account.client_name,
    companyWebsite: account.company_website
  };

  // Construir mensajes con contexto
  const systemPrompt = getAgentSystemPrompt(stageNumber);
  const contextPrompt = buildContextPrompt(
    previousOutputs,
    conversationState,
    accountContext // ← NUEVO: Pasar contexto de cuenta
  );

  const messages = [
    { role: 'system', content: systemPrompt },
    { role: 'system', content: contextPrompt },
    { role: 'user', content: userMessage }
  ];

  // Continuar con llamada a IA...
  const aiResponse = await aiProvider.chat({
    model: account.ai_model,
    messages: messages,
    responseFormat: 'json'
  });

  // ... resto del código
}
```

### 2. Builder de Contexto

```typescript
// /backend/services/contextBuilder.ts

interface AccountContext {
  consultantName: string;
  companyName: string;
  companyWebsite: string | null;
}

function buildContextPrompt(
  previousOutputs: any,
  conversationState: any,
  accountContext: AccountContext
): string {
  let context = "CONTEXTO DE LA CUENTA:\n\n";

  // Información de cuenta (siempre disponible)
  context += `Consultor: ${accountContext.consultantName}\n`;
  context += `Empresa Cliente: ${accountContext.companyName}\n`;
  if (accountContext.companyWebsite) {
    context += `Sitio Web: ${accountContext.companyWebsite}\n`;
  }
  context += "\n";

  // Outputs de agentes anteriores
  if (previousOutputs && Object.keys(previousOutputs).length > 0) {
    context += "OUTPUTS DE AGENTES ANTERIORES:\n\n";

    if (previousOutputs.stage1) {
      context += "AGENTE 1 - BUYER PERSONA:\n";
      context += JSON.stringify(previousOutputs.stage1, null, 2);
      context += "\n\n";
    }

    if (previousOutputs.stage2) {
      context += "AGENTE 2 - BUYER'S JOURNEY:\n";
      context += JSON.stringify(previousOutputs.stage2, null, 2);
      context += "\n\n";
    }

    // ... continuar para otros agentes
  }

  // Estado actual de la conversación
  if (conversationState && Object.keys(conversationState).length > 0) {
    context += "ESTADO ACTUAL DE LA CONVERSACIÓN:\n\n";
    context += JSON.stringify(conversationState, null, 2);
    context += "\n";
  }

  return context;
}
```

### 3. System Prompt Actualizado

En cada agente, el system prompt debe mencionar:

```
INFORMACIÓN DISPONIBLE:

Ya tienes acceso a la siguiente información (NO la preguntes):
- Nombre del consultor: [Se proporciona automáticamente en el contexto]
- Nombre de la empresa cliente: [Se proporciona automáticamente en el contexto]
- Sitio web de la empresa: [Se proporciona automáticamente en el contexto]

Usa esta información cuando sea relevante, especialmente:
- Para personalizar tus mensajes (ej: "Hola [consultantName]...")
- Para referirte a la empresa (ej: "Para [companyName]...")
- Para el output final (ej: en consultantInfo del JSON de output)
```

## Frontend: Crear Cuenta con Website

### Actualizar CreateAccountModal

```typescript
// /frontend/components/dashboard/CreateAccountModal.tsx

interface CreateAccountFormData {
  clientName: string;
  companyWebsite?: string;
  aiModel: AIModel;
}

function CreateAccountModal({ onClose, onSuccess }: Props) {
  const [formData, setFormData] = useState<CreateAccountFormData>({
    clientName: '',
    companyWebsite: '',
    aiModel: 'openai-gpt4o'
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    await accountsService.create({
      clientName: formData.clientName,
      companyWebsite: formData.companyWebsite || null,
      aiModel: formData.aiModel
    });

    onSuccess();
    onClose();
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Nombre del Cliente *
        <input
          type="text"
          value={formData.clientName}
          onChange={e => setFormData({ ...formData, clientName: e.target.value })}
          required
        />
      </label>

      <label>
        Sitio Web del Cliente
        <input
          type="url"
          placeholder="https://ejemplo.com"
          value={formData.companyWebsite}
          onChange={e => setFormData({ ...formData, companyWebsite: e.target.value })}
        />
      </label>

      <label>
        Modelo de IA
        <AIModelSelector
          currentModel={formData.aiModel}
          onChange={model => setFormData({ ...formData, aiModel: model })}
        />
      </label>

      <button type="submit">Crear Cuenta</button>
    </form>
  );
}
```

### Actualizar Endpoint Backend

```typescript
// /backend/controllers/accounts.controller.ts

async function createAccount(req: Request, res: Response) {
  const { clientName, companyWebsite, aiModel } = req.body;
  const { userId } = req.user;

  // Validación
  if (!clientName) {
    return res.status(400).json({ error: 'Nombre del cliente es requerido' });
  }

  // Si hay website, validar formato
  if (companyWebsite && !isValidURL(companyWebsite)) {
    return res.status(400).json({ error: 'URL de sitio web inválida' });
  }

  // Crear cuenta
  const result = await db.query(
    `INSERT INTO accounts (user_id, client_name, company_website, ai_model)
     VALUES ($1, $2, $3, $4)
     RETURNING id, client_name, company_website, ai_model, created_at`,
    [userId, clientName, companyWebsite || null, aiModel || 'openai-gpt4o']
  );

  const account = result.rows[0];

  // Crear 7 stages automáticamente
  await createInitialStages(account.id);

  res.status(201).json(account);
}

function isValidURL(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}
```

## Outputs de Agentes

Cuando un agente genera su output final, debe incluir la información de cuenta:

```typescript
// Ejemplo: Output del Agente 1
{
  "isComplete": true,
  "output": {
    "consultantInfo": {
      "consultantName": "[Obtenido del contexto]",
      "companyName": "[Obtenido del contexto]",
      "companyWebsite": "[Obtenido del contexto]",
      "createdAt": "2024-01-20"
    },
    "scalingUpTable": [ /* ... */ ],
    "buyerPersona": { /* ... */ }
  }
}
```

El backend debe inyectar esta información automáticamente:

```typescript
async function chatWithAgent(req, res) {
  // ... código anterior ...

  if (response.isComplete && response.output) {
    // Inyectar información de cuenta en el output
    response.output.consultantInfo = {
      consultantName: account.consultant_name,
      companyName: account.client_name,
      companyWebsite: account.company_website,
      createdAt: new Date().toISOString()
    };
  }

  res.json(response);
}
```

## Testing

```typescript
describe('Account Context Passing', () => {
  it('debe pasar automáticamente datos de cuenta a agente', async () => {
    const account = await createTestAccount({
      clientName: 'Test Corp',
      companyWebsite: 'https://testcorp.com'
    });

    const response = await chatWithAgent({
      accountId: account.id,
      stageNumber: 1,
      userMessage: 'Hola'
    });

    // Verificar que el agente tiene acceso al contexto
    expect(response.agentMessage).toContain('Test Corp');
  });

  it('debe incluir consultantInfo en output final', async () => {
    // ... completar conversación ...

    const finalResponse = await chatWithAgent({
      accountId: account.id,
      stageNumber: 1,
      userMessage: 'última respuesta'
    });

    expect(finalResponse.isComplete).toBe(true);
    expect(finalResponse.output.consultantInfo).toEqual({
      consultantName: 'Juan Pérez',
      companyName: 'Test Corp',
      companyWebsite: 'https://testcorp.com',
      createdAt: expect.any(String)
    });
  });
});
```

## Migración

Si ya existen cuentas sin `company_website`:

```sql
-- Agregar columna
ALTER TABLE accounts
ADD COLUMN IF NOT EXISTS company_website VARCHAR(500);

-- Las cuentas existentes tendrán NULL, que es válido
-- El consultor puede editarlo después desde Account Settings
```

## UI: Editar Website

Permitir al usuario editar el website desde Account Settings:

```typescript
// /frontend/pages/AccountSettingsPage.tsx

function AccountSettingsPage() {
  const [website, setWebsite] = useState(account.companyWebsite || '');

  const handleUpdateWebsite = async () => {
    await accountsService.update(accountId, {
      companyWebsite: website
    });
    toast.success('Sitio web actualizado');
  };

  return (
    <div>
      <h2>Configuración de Cuenta</h2>

      <label>
        Sitio Web del Cliente
        <input
          type="url"
          value={website}
          onChange={e => setWebsite(e.target.value)}
        />
      </label>

      <button onClick={handleUpdateWebsite}>Guardar</button>
    </div>
  );
}
```

## Resumen

**Antes:**
- Agente 1 preguntaba: nombre consultor, nombre empresa, website (3 preguntas)

**Ahora:**
- Estos datos se recopilan al crear la cuenta
- Se pasan automáticamente a todos los agentes en el contexto
- Agente 1 tiene 3 preguntas menos (27-28 preguntas en total)
- Mejor UX: no repetir información que ya existe
