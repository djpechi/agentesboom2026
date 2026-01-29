# Especificación: Esquema de Base de Datos

## Tecnología

PostgreSQL

## Tablas y Relaciones

### 1. users

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

### 2. accounts (cuentas de clientes)

```sql
CREATE TABLE accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  client_name VARCHAR(255) NOT NULL,
  company_website VARCHAR(500), -- URL del sitio web del cliente
  ai_model VARCHAR(50) NOT NULL DEFAULT 'openai-gpt4o',
  -- Modelos disponibles: 'openai-gpt4o', 'anthropic-claude-opus-4', 'google-gemini-2.5-pro'
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_accounts_user_id ON accounts(user_id);
CREATE INDEX idx_accounts_ai_model ON accounts(ai_model);
```

### 3. stages (etapas del pipeline)

```sql
CREATE TABLE stages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  stage_number INTEGER NOT NULL CHECK (stage_number BETWEEN 1 AND 7),
  status VARCHAR(50) NOT NULL DEFAULT 'locked',
  -- Estados: 'locked', 'unlocked', 'in_progress', 'completed', 'invalidated'
  ai_model_used VARCHAR(50), -- Modelo de IA usado en esta sesión (para debugging/referencia)
  conversation_state JSONB, -- Estado actual de la conversación con el agente
  output JSONB, -- Output generado por el agente
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(account_id, stage_number)
);

CREATE INDEX idx_stages_account_id ON stages(account_id);
CREATE INDEX idx_stages_status ON stages(status);
CREATE INDEX idx_stages_ai_model_used ON stages(ai_model_used);
```

### 4. conversation_history (historial de mensajes)

```sql
CREATE TABLE conversation_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  stage_id UUID NOT NULL REFERENCES stages(id) ON DELETE CASCADE,
  role VARCHAR(50) NOT NULL, -- 'user' o 'assistant'
  content TEXT NOT NULL,
  metadata JSONB, -- Información adicional del mensaje
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversation_history_stage_id ON conversation_history(stage_id);
CREATE INDEX idx_conversation_history_created_at ON conversation_history(created_at);
```

## Relaciones

```
users (1) ──┐
            │
            └─> (N) accounts (1) ──┐
                                   │
                                   └─> (7) stages (1) ──┐
                                                         │
                                                         └─> (N) conversation_history
```

## Estados de Stages

| Estado | Descripción | Transiciones Permitidas |
|--------|-------------|------------------------|
| `locked` | No se puede acceder | → `unlocked` (cuando la anterior se completa) |
| `unlocked` | Puede iniciarse | → `in_progress` (al entrar) |
| `in_progress` | Conversación activa | → `completed` (al terminar) |
| `completed` | Terminada con output | → `in_progress` (al editar), → `invalidated` (si anterior se edita) |
| `invalidated` | Requiere rehacerse | → `in_progress` (al rehacer) |

## Lógica de Desbloqueo

```javascript
// Al completar stage N:
1. Marcar stage N como 'completed'
2. Desbloquear stage N+1 (cambiar de 'locked' a 'unlocked')

// Al editar stage N (ya completada):
1. Cambiar stage N a 'in_progress'
2. Cambiar stages N+1 hasta 7 a 'invalidated'
3. Limpiar outputs de stages N+1 hasta 7
```

## Inicialización de Cuenta

Al crear una nueva cuenta:

```sql
-- Crear 7 stages automáticamente
INSERT INTO stages (account_id, stage_number, status)
VALUES
  ('{account_id}', 1, 'unlocked'),  -- Solo la primera desbloqueada
  ('{account_id}', 2, 'locked'),
  ('{account_id}', 3, 'locked'),
  ('{account_id}', 4, 'locked'),
  ('{account_id}', 5, 'locked'),
  ('{account_id}', 6, 'locked'),
  ('{account_id}', 7, 'locked');
```

## Campos JSONB

### conversation_state (ejemplo)

```json
{
  "currentQuestion": 5,
  "totalQuestions": 10,
  "collectedData": {
    "industry": "Software B2B",
    "companySize": "50-200 empleados",
    "painPoints": ["..."]
  },
  "progress": 50
}
```

### output (ejemplo - Agente 1)

```json
{
  "buyerPersona": {
    "name": "Carlos el CTO",
    "age": 38,
    "role": "Chief Technology Officer",
    "goals": ["..."],
    "painPoints": ["..."],
    "narrative": "Carlos es un CTO de una empresa..."
  },
  "scalingUpTable": [
    {
      "category": "Identificadores",
      "data": "..."
    }
  ]
}
```

## Migraciones

Crear archivos de migración:
- `001_create_users_table.sql`
- `002_create_accounts_table.sql`
- `003_create_stages_table.sql`
- `004_create_conversation_history_table.sql`
- `005_create_indexes.sql`
- `006_add_ai_model_to_accounts.sql` (si se agrega después)
- `007_add_ai_model_used_to_stages.sql` (si se agrega después)

## Queries Comunes

```sql
-- Obtener todas las cuentas de un usuario con progreso
SELECT
  a.id,
  a.client_name,
  COUNT(CASE WHEN s.status = 'completed' THEN 1 END) as completed_stages,
  MAX(s.updated_at) as last_activity
FROM accounts a
LEFT JOIN stages s ON a.id = s.account_id
WHERE a.user_id = '{user_id}'
GROUP BY a.id, a.client_name
ORDER BY last_activity DESC;

-- Obtener pipeline completo de una cuenta
SELECT
  stage_number,
  status,
  output,
  completed_at
FROM stages
WHERE account_id = '{account_id}'
ORDER BY stage_number;

-- Obtener historial de conversación de una etapa
SELECT role, content, created_at
FROM conversation_history
WHERE stage_id = '{stage_id}'
ORDER BY created_at ASC;
```
