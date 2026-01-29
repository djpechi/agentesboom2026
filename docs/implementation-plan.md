# Plan de Implementación - BOOMS Platform

## Metodología: Ralph Wiggum

Este proyecto sigue la técnica Ralph Wiggum, que utiliza agentes de IA para planificar e implementar features iterativamente. Este documento es el plan maestro de implementación.

## Fases del Proyecto

### Fase 0: Setup Inicial (1-2 días)

#### 0.1 Configuración de Repositorio
- [ ] Crear repositorio Git
- [ ] Configurar `.gitignore`
- [ ] Crear estructura de directorios base
- [ ] Configurar ESLint + Prettier
- [ ] Crear README.md inicial

#### 0.2 Configuración de Base de Datos
- [ ] Instalar PostgreSQL localmente o configurar servicio cloud
- [ ] Crear base de datos `booms_dev`
- [ ] Configurar pool de conexiones

#### 0.3 Configuración de Backend
- [ ] Inicializar proyecto Python con Poetry
- [ ] Crear estructura de carpetas backend (FastAPI)
- [ ] Instalar dependencias base (fastapi, uvicorn, sqlalchemy, asyncpg)
- [ ] Configurar pyproject.toml
- [ ] Configurar pydantic-settings para variables de entorno
- [ ] Configurar alembic para migraciones

#### 0.4 Configuración de Frontend
- [ ] Inicializar proyecto React con Vite + TypeScript
- [ ] Instalar Tailwind CSS
- [ ] Instalar shadcn/ui
- [ ] Configurar React Router
- [ ] Crear estructura de carpetas frontend

#### 0.5 Variables de Entorno
- [ ] Crear `.env.example` con todas las variables necesarias
- [ ] Configurar API keys de OpenAI, Anthropic, Google
- [ ] Configurar JWT_SECRET
- [ ] Configurar DATABASE_URL

---

### Fase 1: Base de Datos y Autenticación (2-3 días)

#### 1.1 Migraciones de Base de Datos (Alembic)
- [ ] Crear modelos SQLAlchemy (User, Account, Stage, ConversationHistory)
- [ ] Generar migración inicial: `alembic revision --autogenerate -m "initial"`
- [ ] Revisar y ajustar migración generada
- [ ] Ejecutar migración: `alembic upgrade head`
- [ ] Crear migración para documents table (RAG): `alembic revision -m "add documents"`

#### 1.2 Backend - Sistema de Autenticación (FastAPI)
- [ ] Crear schemas Pydantic (UserCreate, UserLogin, TokenResponse)
- [ ] Implementar AuthService (register, login, verify_token)
- [ ] Crear dependency `get_current_user`
- [ ] Implementar router `POST /api/auth/register`
- [ ] Implementar router `POST /api/auth/login`
- [ ] Implementar router `GET /api/auth/me`
- [ ] Tests con pytest y httpx

#### 1.3 Frontend - Autenticación
- [ ] Crear `AuthContext`
- [ ] Crear página `LoginPage`
- [ ] Crear página `RegisterPage`
- [ ] Crear componente `PrivateRoute`
- [ ] Implementar `authService` (API calls)
- [ ] Configurar axios con interceptores

#### 1.4 Testing Autenticación
- [ ] Probar registro de usuario
- [ ] Probar login exitoso
- [ ] Probar login con credenciales inválidas
- [ ] Probar token expirado
- [ ] Probar rutas protegidas

---

### Fase 2: Gestión de Cuentas (2-3 días)

#### 2.1 Backend - CRUD de Cuentas (FastAPI)
- [ ] Crear schemas Pydantic (AccountCreate, AccountUpdate, AccountResponse)
- [ ] Crear modelo SQLAlchemy Account con relaciones
- [ ] Implementar AccountService
- [ ] Implementar routers de accounts
- [ ] Dependency para verificar ownership de account
- [ ] Tests con pytest

#### 2.2 Inicialización de Stages
- [ ] Trigger automático: al crear account, crear 7 stages
- [ ] Stage 1 debe tener status `unlocked`
- [ ] Stages 2-7 deben tener status `locked`
- [ ] Tests de inicialización

#### 2.3 Frontend - Dashboard
- [ ] Crear página `DashboardPage`
- [ ] Crear componente `AccountCard`
- [ ] Crear componente `AccountList`
- [ ] Crear componente `CreateAccountModal` (incluir campo company_website)
- [ ] Implementar `accountsService`
- [ ] Hook `useAccounts`
- [ ] Filtrado y búsqueda de cuentas
- [ ] Account Settings page (editar company_website)

#### 2.4 Testing Gestión de Cuentas
- [ ] Crear cuenta y verificar 7 stages creadas
- [ ] Editar nombre de cuenta
- [ ] Eliminar cuenta (verificar cascade)
- [ ] Ver lista de cuentas con progreso

---

### Fase 3: AI Provider Service (3-4 días)

#### 3.1 Backend - Servicio Unificado de IA (Python)
- [ ] Implementar `AIProviderService` con async/await
- [ ] Integración con OpenAI SDK (AsyncOpenAI)
- [ ] Integración con Anthropic SDK (AsyncAnthropic)
- [ ] Integración con Google Generative AI
- [ ] Normalización de respuestas entre providers
- [ ] Manejo de errores async
- [ ] Tests con pytest-asyncio y mocks

#### 3.2 Endpoints de Configuración de Modelo
- [ ] Implementar `GET /api/accounts/:accountId/ai-model`
- [ ] Implementar `PUT /api/accounts/:accountId/ai-model`
- [ ] Validación de modelos permitidos

#### 3.3 Frontend - Selector de Modelo
- [ ] Crear componente `AIModelSelector`
- [ ] Integrar en `AccountSettings`
- [ ] Mostrar selector al crear nueva cuenta
- [ ] Actualizar modelo desde settings

#### 3.4 Testing AI Provider
- [ ] Test: Llamada a OpenAI retorna formato correcto
- [ ] Test: Llamada a Anthropic retorna formato correcto
- [ ] Test: Llamada a Google retorna formato correcto
- [ ] Test: Error handling de rate limits
- [ ] Test: Error handling de API keys inválidas

---

### Fase 4: Prompts de Agentes (3-4 días)

#### 4.1 System Prompts para Cada Agente
- [ ] Adaptar prompt Agente 1: Booms, the Buyer Persona Architect (desde Relevance)
- [ ] Adaptar prompt Agente 2: Arquitecto de Buyer's Journey (desde Relevance)
- [ ] Adaptar prompt Agente 3: Agente de Ofertas 100M (desde Relevance)
- [ ] Adaptar prompt Agente 4: Selector de Canales (desde Relevance)
- [ ] Adaptar prompt Agente 5: Atlas, the AEO Strategist (desde Relevance)
- [ ] Adaptar prompt Agente 6: Planner, the Content Strategist (desde Relevance)
- [ ] Adaptar prompt Agente 7: Agente de Budgets para Pauta (desde Relevance)

#### 4.2 Prompt Engineering
- [ ] Agregar formato JSON obligatorio a cada prompt
- [ ] Definir estructura de `updatedState` para cada agente
- [ ] Definir criterios de completitud (cuándo `isComplete = true`)
- [ ] Agregar instrucciones STATELESS a cada prompt
- [ ] Testing de prompts con IA real
- [ ] Refinamiento basado en resultados

#### 4.3 Documentación de Outputs
- [ ] Documentar estructura JSON de output de cada agente
- [ ] Crear ejemplos de outputs esperados
- [ ] Validadores de schema (Zod) para cada output

#### 4.4 Configuración de Capabilities
- [ ] Mapear qué agentes usan Google Search
- [ ] Mapear qué agentes usan RAG/documentos
- [ ] Crear archivo de configuración `agentCapabilities.ts`

---

### Fase 5: Sistema de Tools (2-3 días)

#### 5.1 Perplexity Search Integration (PRINCIPAL)
- [ ] Configurar Perplexity API key
- [ ] Implementar `PerplexitySearchService` con httpx async
- [ ] Implementar función `search(query, search_depth)`
- [ ] Testing de búsquedas con diferentes queries
- [ ] Manejo de rate limits y errores

#### 11.2 Tool System
- [ ] Implementar sistema de tools genérico
- [ ] Actualizar `AIProviderService` para soportar function calling
- [ ] Implementar function calling para OpenAI
- [ ] Implementar tool use para Anthropic
- [ ] Implementar function calling para Google Gemini
- [ ] Crear configuración de tools por agente

#### 11.3 Tool Execution Loop
- [ ] Implementar loop de ejecución de tools
- [ ] Manejo de múltiples tool calls
- [ ] Prevención de loops infinitos
- [ ] Error handling de tool failures

#### 11.4 Testing Tools
- [ ] Test: Google Search retorna resultados válidos
- [ ] Test: Agente usa tool cuando es necesario
- [ ] Test: Resultados de tools se integran en respuesta
- [ ] Test: Error handling de tool failures

#### 11.5 (Opcional) Logging de Tool Usage
- [ ] Crear tabla `tool_usage` en BD
- [ ] Guardar qué tools se usaron y cuándo
- [ ] Analytics de uso de tools

---

### Fase 6: Sistema RAG (3-4 días)

#### 10.1 Vector Database Setup
- [ ] Decidir: Pinecone vs PostgreSQL+pgvector vs ChromaDB
- [ ] Configurar vector database
- [ ] Crear tabla/índice de documentos
- [ ] Instalar extensión pgvector (si se usa PostgreSQL)

#### 10.2 Document Ingestion Pipeline (Python)
- [ ] Instalar dependencias (pypdf, langchain, sentence-transformers)
- [ ] Implementar `DocumentIngestionService` async
- [ ] Función para extraer texto de PDFs (pypdf)
- [ ] Implementar chunking con Langchain RecursiveCharacterTextSplitter
- [ ] Generar embeddings (OpenAI text-embedding-3-small via API o sentence-transformers local)
- [ ] Almacenar chunks en PostgreSQL con pgvector

#### 10.3 Retrieval System (Python)
- [ ] Implementar `RAGService` async
- [ ] Función `search_documents(query, agent_id)` con similitud vectorial
- [ ] Búsqueda por similitud usando pgvector cosine distance
- [ ] Filtrado por agente
- [ ] Ranking de resultados

#### 10.4 Integración con Agentes
- [ ] Opción 1: RAG automático (inyectar docs relevantes en contexto)
- [ ] Opción 2: RAG como tool (agente decide cuándo usar)
- [ ] Implementar opción elegida

#### 10.5 Document Management
- [ ] Crear directorio `data/pdfs/`
- [ ] Organizar PDFs por agente
- [ ] Script de ingesta inicial
- [ ] Ejecutar ingesta de todos los documentos

#### 10.6 Testing RAG
- [ ] Test: Ingesta de PDF funciona correctamente
- [ ] Test: Búsqueda retorna documentos relevantes
- [ ] Test: Agente usa información de documentos en respuestas
- [ ] Test: Calidad de respuestas con RAG vs sin RAG

#### 10.7 (Opcional) Admin UI para Documentos
- [ ] Endpoint `POST /api/admin/documents` (upload)
- [ ] Endpoint `GET /api/admin/documents/:agentId`
- [ ] Componente `DocumentUpload`
- [ ] Componente `DocumentList`

---

### Fase 7: Sistema de Chat con Agentes (4-5 días)

#### 11.1 Backend - Endpoint de Chat
- [ ] Implementar `POST /api/agents/chat`
- [ ] Implementar `buildContextPrompt` function
- [ ] **Paso automático de contexto de cuenta** (consultantName, companyName, companyWebsite)
- [ ] Incluir outputs de agentes anteriores en contexto
- [ ] Guardar mensajes en `conversation_history`
- [ ] Actualizar `conversation_state` en stage
- [ ] Actualizar `ai_model_used` en stage
- [ ] Inyectar `consultantInfo` automáticamente en outputs finales

#### 11.2 Backend - Gestión de Stages
- [ ] Implementar `GET /api/accounts/:accountId/stages`
- [ ] Implementar `GET /api/stages/:stageId`
- [ ] Implementar `PUT /api/stages/:stageId/start`
- [ ] Implementar `PUT /api/stages/:stageId/complete`
- [ ] Implementar `PUT /api/stages/:stageId/reset`
- [ ] Implementar `GET /api/stages/:stageId/history`

#### 11.3 Lógica de Desbloqueo
- [ ] Al completar stage N, desbloquear N+1
- [ ] Al resetear stage N, invalidar N+1 hasta 7
- [ ] Tests de lógica de desbloqueo

#### 11.4 Frontend - Interfaz de Chat
- [ ] Crear página `ChatPage`
- [ ] Crear componente `ChatInterface`
- [ ] Crear componente `MessageBubble`
- [ ] Crear componente `ChatInput`
- [ ] Crear componente `ProgressBar`
- [ ] Hook `useChat`
- [ ] Implementar `chatService`

#### 11.5 Frontend - Pipeline View
- [ ] Crear página `AccountDetailPage`
- [ ] Crear componente `PipelineView`
- [ ] Crear componente `StageCard`
- [ ] Crear componente `StageStatusBadge`
- [ ] Lógica de navegación según status
- [ ] Visual de progreso general

#### 11.6 Testing Sistema de Chat
- [ ] Test: Conversación completa Agente 1
- [ ] Test: Output se guarda correctamente
- [ ] Test: Stage 2 se desbloquea al completar 1
- [ ] Test: Contexto se pasa correctamente a Agente 2
- [ ] Test: Reset de stage invalida posteriores
- [ ] Test: No se puede acceder a stage locked

---

### Fase 8: Sistema de Exportación (3-4 días)

#### 10.1 Backend - Servicio de Exportación
- [ ] Implementar `ExportService`
- [ ] Configurar Puppeteer
- [ ] Método `generatePDF(stageId)`
- [ ] Método `generateExcel(stageId)`
- [ ] Método `generateCompletePackage(accountId)`

#### 10.2 Templates PDF
- [ ] Crear template HTML para Agente 1
- [ ] Crear template HTML para Agente 2
- [ ] Crear template HTML para Agente 3
- [ ] Crear template HTML para Agente 4
- [ ] Crear template HTML para Agente 5
- [ ] Crear template HTML para Agente 6
- [ ] Crear template HTML para Agente 7

#### 10.3 Generadores Excel
- [ ] Implementar Excel para Agente 1
- [ ] Implementar Excel para Agente 2
- [ ] Implementar Excel para Agente 4
- [ ] Implementar Excel para Agente 5
- [ ] Implementar Excel para Agente 6
- [ ] Implementar Excel para Agente 7

#### 10.4 Endpoints de Exportación
- [ ] Implementar `GET /api/exports/stages/:stageId/pdf`
- [ ] Implementar `GET /api/exports/stages/:stageId/excel`
- [ ] Implementar `GET /api/exports/accounts/:accountId/all`

#### 10.5 Frontend - Descarga de Entregables
- [ ] Crear página `OutputPage`
- [ ] Crear componente `OutputView`
- [ ] Crear componente `ExportButtons`
- [ ] Crear componente `OutputRenderer`
- [ ] Lógica de descarga de archivos

#### 10.6 Testing Exportación
- [ ] Test: PDF se genera correctamente para cada agente
- [ ] Test: Excel se genera correctamente
- [ ] Test: ZIP contiene todos los archivos
- [ ] Test: Nombres de archivo son correctos

---

### Fase 9: Refinamiento y Optimización (2-3 días)

#### 11.1 UX/UI Polish
- [ ] Animaciones y transiciones
- [ ] Loading states consistentes
- [ ] Error messages amigables
- [ ] Tooltips explicativos
- [ ] Responsive design (mobile)
- [ ] Dark mode (opcional)

#### 11.2 Performance
- [ ] Optimizar queries de base de datos
- [ ] Implementar cache de browser Puppeteer
- [ ] Lazy loading de componentes React
- [ ] Code splitting
- [ ] Optimización de imágenes

#### 11.3 Manejo de Errores
- [ ] Error boundaries en React
- [ ] Toast notifications
- [ ] Retry logic para llamadas de IA
- [ ] Fallbacks para modelos de IA no disponibles

#### 11.4 Validaciones
- [ ] Validación de formularios con Zod
- [ ] Validación de outputs de agentes
- [ ] Sanitización de inputs

---

### Fase 10: Testing End-to-End (2-3 días)

#### 10.1 Setup de Testing
- [ ] Configurar Jest para backend
- [ ] Configurar React Testing Library
- [ ] Configurar Playwright o Cypress (E2E)

#### 10.2 Tests E2E Críticos
- [ ] Test: Flujo completo de onboarding (7 etapas)
- [ ] Test: Crear cuenta → Completar Agente 1 → Descargar PDF
- [ ] Test: Editar stage anterior invalida posteriores
- [ ] Test: Cambio de modelo de IA funciona
- [ ] Test: Exportar paquete completo

#### 10.3 Tests de Integración
- [ ] Test: Auth + Accounts
- [ ] Test: Accounts + Stages
- [ ] Test: Stages + Chat
- [ ] Test: Chat + AI Providers
- [ ] Test: Stages + Exports

---

### Fase 11: Deployment (2-3 días)

#### 11.1 Preparación Backend
- [ ] Configurar variables de entorno para producción
- [ ] Configurar CORS
- [ ] Rate limiting
- [ ] Helmet.js (security headers)
- [ ] Logging (Winston, Morgan)

#### 11.2 Preparación Frontend
- [ ] Build de producción
- [ ] Configurar variables de entorno
- [ ] Optimizar bundle size
- [ ] Generar sourcemaps

#### 11.3 Base de Datos Producción
- [ ] Configurar PostgreSQL en servidor
- [ ] Ejecutar migraciones en producción
- [ ] Backup automático
- [ ] Connection pooling

#### 11.4 Deployment
- [ ] Opción 1: Deploy en Heroku
- [ ] Opción 2: Deploy en Railway
- [ ] Opción 3: Deploy en Render
- [ ] Opción 4: Deploy en VPS (DigitalOcean, AWS)
- [ ] Configurar HTTPS
- [ ] Configurar dominio

#### 11.5 Monitoring
- [ ] Error tracking (Sentry)
- [ ] Analytics (Plausible, Google Analytics)
- [ ] Uptime monitoring
- [ ] Performance monitoring

---

## Dependencias entre Fases

```
Fase 0 (Setup)
    ↓
Fase 1 (Auth + DB)
    ↓
Fase 2 (Accounts)
    ↓
Fase 3 (AI Provider) ← Fase 4 (Prompts)
    ↓                      ↓
Fase 5 (Tools) ←──────────┘
    ↓
Fase 6 (RAG)
    ↓
Fase 7 (Chat System) ← integra Tools + RAG
    ↓
Fase 8 (Exports)
    ↓
Fase 9 (Refinamiento)
    ↓
Fase 10 (Testing)
    ↓
Fase 11 (Deployment)
```

## Estimación Total

- **Tiempo Estimado**: 25-35 días de desarrollo
- **Equipo**: 1-2 desarrolladores full-stack
- **Horas**: ~200-280 horas

**Nota**: La estimación aumentó por la inclusión de:
- Sistema de Tools/Function Calling (+2-3 días)
- Sistema RAG con vector database (+3-4 días)

## Próximos Pasos Inmediatos

1. **Configurar entorno de desarrollo**
   - Instalar PostgreSQL
   - Configurar API keys de OpenAI, Anthropic, Google
   - Inicializar repositorio Git

2. **Comenzar Fase 0**
   - Crear estructura de carpetas
   - Configurar backend con TypeScript
   - Configurar frontend con Vite + React

3. **Ejecutar primera migración**
   - Crear tabla `users`
   - Implementar endpoint de registro

## Uso con Ralph Wiggum

Para aplicar la técnica Ralph Wiggum:

1. Cada fase puede ejecutarse mediante un agente de IA
2. El agente lee las especificaciones en `spec/topics/`
3. El agente implementa los items marcados en esta lista
4. Cada implementación se valida con tests
5. Se pasa a la siguiente fase solo cuando la actual está completa

### Comando Ejemplo

```bash
# Pseudocódigo del loop de Ralph Wiggum
while [ true ]; do
  echo "Fase actual: $(get_current_phase)"
  echo "Tasks pendientes: $(get_pending_tasks)"

  # Llamar al agente de IA
  claude "Implementa el siguiente task del plan: $(get_next_task).
         Usa las especificaciones en spec/topics/.
         Ejecuta tests después de implementar."

  # Si todos los tests pasan, continuar
  if [ $? -eq 0 ]; then
    mark_task_complete
  else
    echo "Tests fallaron. Corrigiendo..."
  fi
done
```

## Criterios de Aceptación por Fase

Cada fase se considera completa cuando:

- ✅ Todos los items de la checklist están marcados
- ✅ Tests unitarios pasan (coverage > 80%)
- ✅ Tests de integración pasan
- ✅ No hay errores de TypeScript
- ✅ Lint pasa sin warnings
- ✅ Funcionalidad validada manualmente

## Recursos de Referencia

- Especificaciones técnicas: `spec/topics/`
- Jobs to Be Done: `spec/jtbd/`
- Documentación: `docs/`
- README principal: `README.md`
