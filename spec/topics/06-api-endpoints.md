# Especificación: API Endpoints Completos

## Base URL

```
/api
```

## Autenticación

Todos los endpoints (excepto `/auth/*`) requieren header de autenticación:

```
Authorization: Bearer {jwt_token}
```

---

## 1. Autenticación

### POST /auth/register

Registrar nuevo usuario.

**Request:**
```json
{
  "email": "consultor@blackandorange.com",
  "password": "SecurePass123!",
  "fullName": "Juan Pérez"
}
```

**Response (201):**
```json
{
  "user": {
    "id": "uuid",
    "email": "consultor@blackandorange.com",
    "fullName": "Juan Pérez"
  },
  "token": "eyJhbGciOiJIUzI..."
}
```

**Errores:**
- `400`: Validación fallida
- `409`: Email ya registrado

---

### POST /auth/login

Iniciar sesión.

**Request:**
```json
{
  "email": "consultor@blackandorange.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "user": {
    "id": "uuid",
    "email": "consultor@blackandorange.com",
    "fullName": "Juan Pérez"
  },
  "token": "eyJhbGciOiJIUzI..."
}
```

**Errores:**
- `401`: Credenciales inválidas

---

### GET /auth/me

Obtener usuario actual (validar token).

**Response (200):**
```json
{
  "id": "uuid",
  "email": "consultor@blackandorange.com",
  "fullName": "Juan Pérez"
}
```

**Errores:**
- `401`: Token inválido o expirado

---

## 2. Cuentas (Accounts)

### GET /accounts

Listar todas las cuentas del usuario autenticado.

**Query Params (opcionales):**
- `search`: Buscar por nombre de cliente
- `sortBy`: `created_at` | `last_activity` | `progress` (default: `last_activity`)
- `order`: `asc` | `desc` (default: `desc`)

**Response (200):**
```json
{
  "accounts": [
    {
      "id": "uuid",
      "clientName": "Empresa XYZ",
      "aiModel": "openai-gpt4o",
      "completedStages": 3,
      "totalStages": 7,
      "lastActivity": "2024-01-15T10:30:00Z",
      "createdAt": "2024-01-10T08:00:00Z"
    }
  ]
}
```

---

### POST /accounts

Crear nueva cuenta.

**Request:**
```json
{
  "clientName": "Empresa ABC",
  "aiModel": "openai-gpt4o"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "userId": "uuid",
  "clientName": "Empresa ABC",
  "aiModel": "openai-gpt4o",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

**Nota**: Al crear una cuenta, automáticamente se crean las 7 stages con status `locked` (excepto stage 1 que es `unlocked`).

**Errores:**
- `400`: Validación fallida

---

### GET /accounts/:accountId

Obtener detalle de una cuenta específica.

**Response (200):**
```json
{
  "id": "uuid",
  "clientName": "Empresa ABC",
  "aiModel": "openai-gpt4o",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

**Errores:**
- `404`: Cuenta no encontrada
- `403`: No autorizado

---

### PUT /accounts/:accountId

Actualizar cuenta.

**Request:**
```json
{
  "clientName": "Empresa ABC S.A.",
  "aiModel": "anthropic-claude-opus-4"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "clientName": "Empresa ABC S.A.",
  "aiModel": "anthropic-claude-opus-4",
  "updatedAt": "2024-01-16T09:00:00Z"
}
```

**Errores:**
- `404`: Cuenta no encontrada
- `403`: No autorizado
- `400`: Datos inválidos

---

### DELETE /accounts/:accountId

Eliminar cuenta (y todas sus stages/conversaciones).

**Response (204):**
```
No content
```

**Errores:**
- `404`: Cuenta no encontrada
- `403`: No autorizado

---

### GET /accounts/:accountId/ai-model

Obtener modelo de IA configurado.

**Response (200):**
```json
{
  "aiModel": "openai-gpt4o"
}
```

---

### PUT /accounts/:accountId/ai-model

Cambiar modelo de IA.

**Request:**
```json
{
  "aiModel": "anthropic-claude-opus-4"
}
```

**Response (200):**
```json
{
  "success": true,
  "aiModel": "anthropic-claude-opus-4"
}
```

**Errores:**
- `400`: Modelo no válido

---

## 3. Stages (Etapas)

### GET /accounts/:accountId/stages

Obtener todas las stages de una cuenta (pipeline completo).

**Response (200):**
```json
{
  "stages": [
    {
      "id": "uuid",
      "stageNumber": 1,
      "status": "completed",
      "aiModelUsed": "openai-gpt4o",
      "completedAt": "2024-01-15T12:00:00Z",
      "output": { "buyerPersona": {...}, "scalingUpTable": [...] }
    },
    {
      "id": "uuid",
      "stageNumber": 2,
      "status": "unlocked",
      "aiModelUsed": null,
      "completedAt": null,
      "output": null
    },
    {
      "id": "uuid",
      "stageNumber": 3,
      "status": "locked",
      "aiModelUsed": null,
      "completedAt": null,
      "output": null
    }
    // ... stages 4-7
  ]
}
```

---

### GET /stages/:stageId

Obtener detalle de una stage específica.

**Response (200):**
```json
{
  "id": "uuid",
  "accountId": "uuid",
  "stageNumber": 1,
  "status": "completed",
  "aiModelUsed": "openai-gpt4o",
  "conversationState": {...},
  "output": {...},
  "startedAt": "2024-01-15T10:00:00Z",
  "completedAt": "2024-01-15T12:00:00Z"
}
```

**Errores:**
- `404`: Stage no encontrada
- `403`: No autorizado

---

### PUT /stages/:stageId/start

Marcar stage como `in_progress`.

**Response (200):**
```json
{
  "id": "uuid",
  "status": "in_progress",
  "startedAt": "2024-01-15T10:00:00Z"
}
```

**Errores:**
- `400`: Stage no está desbloqueada

---

### PUT /stages/:stageId/complete

Marcar stage como `completed` y desbloquear la siguiente.

**Request:**
```json
{
  "output": {
    "buyerPersona": {...},
    "scalingUpTable": [...]
  }
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "status": "completed",
  "output": {...},
  "completedAt": "2024-01-15T12:00:00Z"
}
```

**Side effects:**
- Desbloquea stage N+1 (cambia de `locked` a `unlocked`)

**Errores:**
- `400`: Stage no está en progreso

---

### PUT /stages/:stageId/reset

Reiniciar stage (para edición). Invalida stages posteriores.

**Response (200):**
```json
{
  "id": "uuid",
  "status": "in_progress",
  "invalidatedStages": [3, 4, 5, 6, 7]
}
```

**Side effects:**
- Stages N+1 hasta 7 cambian a `invalidated`
- Se limpian outputs de stages invalidadas

**Errores:**
- `400`: Stage no puede resetearse

---

### GET /stages/:stageId/history

Obtener historial de conversación de una stage.

**Response (200):**
```json
{
  "messages": [
    {
      "id": "uuid",
      "role": "assistant",
      "content": "Hola, soy Booms...",
      "createdAt": "2024-01-15T10:00:00Z"
    },
    {
      "id": "uuid",
      "role": "user",
      "content": "Vendo software B2B",
      "createdAt": "2024-01-15T10:01:00Z"
    }
  ]
}
```

---

## 4. Agentes de IA

### POST /agents/chat

Enviar mensaje a un agente y recibir respuesta.

**Request:**
```json
{
  "accountId": "uuid",
  "stageId": "uuid",
  "stageNumber": 1,
  "userMessage": "Vendemos software de gestión de proyectos",
  "conversationState": {
    "currentQuestion": 2,
    "collectedData": {...}
  },
  "previousOutputs": {
    // Outputs de stages anteriores (si aplica)
  }
}
```

**Response (200):**
```json
{
  "agentMessage": "Excelente. ¿Cuál es el tamaño típico de empresas que compran?",
  "updatedState": {
    "currentQuestion": 3,
    "collectedData": {
      "product": "Software de gestión de proyectos"
    }
  },
  "progress": 30,
  "isComplete": false,
  "output": null,
  "metadata": {
    "modelUsed": "openai-gpt4o",
    "provider": "openai",
    "usage": {
      "promptTokens": 1234,
      "completionTokens": 567,
      "totalTokens": 1801
    }
  }
}
```

**Cuando `isComplete: true`:**
```json
{
  "agentMessage": "Perfecto, he completado tu buyer persona.",
  "updatedState": {...},
  "progress": 100,
  "isComplete": true,
  "output": {
    "buyerPersona": {...},
    "scalingUpTable": [...]
  },
  "metadata": {...}
}
```

**Errores:**
- `400`: Datos inválidos
- `403`: No autorizado
- `500`: Error del modelo de IA

---

## 5. Exportación

### GET /exports/stages/:stageId/pdf

Generar y descargar PDF del output de una stage.

**Response (200):**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="EmpresaXYZ_Stage1_BuyerPersona.pdf"

[Binary PDF data]
```

**Errores:**
- `404`: Stage no encontrada o sin output
- `403`: No autorizado

---

### GET /exports/stages/:stageId/excel

Generar y descargar Excel del output de una stage (para stages con datos tabulares).

**Response (200):**
```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="EmpresaXYZ_Stage2_BuyersJourney.xlsx"

[Binary Excel data]
```

**Errores:**
- `404`: Stage no encontrada o sin output
- `400`: Stage no soporta formato Excel
- `403`: No autorizado

---

### GET /exports/accounts/:accountId/all

Generar y descargar ZIP con todos los entregables completados.

**Response (200):**
```
Content-Type: application/zip
Content-Disposition: attachment; filename="EmpresaXYZ_OnboardingCompleto.zip"

[Binary ZIP data containing all PDFs and Excels]
```

**Errores:**
- `404`: Cuenta no encontrada
- `400`: Ninguna stage completada
- `403`: No autorizado

---

## Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Operación exitosa |
| 201 | Created - Recurso creado exitosamente |
| 204 | No Content - Operación exitosa sin contenido de respuesta |
| 400 | Bad Request - Validación fallida o datos inválidos |
| 401 | Unauthorized - No autenticado (token inválido/faltante) |
| 403 | Forbidden - Autenticado pero no autorizado (no es owner del recurso) |
| 404 | Not Found - Recurso no existe |
| 409 | Conflict - Conflicto (ej: email ya existe) |
| 500 | Internal Server Error - Error del servidor |

---

## Formato de Errores

Todos los errores siguen este formato:

```json
{
  "error": "Mensaje de error legible para el usuario",
  "code": "ERROR_CODE",
  "details": {
    // Información adicional (opcional)
  }
}
```

Ejemplo:

```json
{
  "error": "Credenciales inválidas",
  "code": "INVALID_CREDENTIALS"
}
```

```json
{
  "error": "Validación fallida",
  "code": "VALIDATION_ERROR",
  "details": {
    "email": "Email inválido",
    "password": "Debe tener al menos 8 caracteres"
  }
}
```
