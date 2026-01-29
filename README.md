# BOOMS Platform 🎯

**AI-Powered Marketing Onboarding Platform**

[![Backend](https://img.shields.io/badge/Backend-FastAPI-green)](http://localhost:8000/docs)
[![Frontend](https://img.shields.io/badge/Frontend-React-blue)](http://localhost:5173)
[![Status](https://img.shields.io/badge/Status-MVP_Ready-success)]()

## 🎉 MVP Completado

El **MVP de BOOMS Platform** está 100% funcional con Agentes 1-2 implementados, sistema de autenticación, gestión de cuentas, chat AI, y exportación PDF/Excel.

### ✅ Funcionalidades Implementadas

- 🔐 **Autenticación JWT** - Login, registro, protección de rutas
- 🏢 **Gestión de Cuentas** - CRUD completo para clientes
- 🎯 **Sistema de Stages** - 7 etapas secuenciales con desbloqueo automático
- 🤖 **Agente 1 (BOOMS)** - Análisis de marca y mercado con GPT-4o
- 🗺️ **Agente 2 (Journey)** - Customer Journey Mapping con Perplexity
- 💬 **Chat Interface** - Interfaz moderna de conversación con AI
- 📄 **Export PDF** - Reportes profesionales con WeasyPrint
- 📊 **Export Excel** - Workbooks multi-hoja con openpyxl
- 💾 **Arquitectura STATELESS** - Estado completo en JSONB
- 🚀 **Frontend React** - UI moderna con Tailwind CSS

## 🚀 Quick Start

### Prerrequisitos

```bash
# Verificar versiones
python --version  # 3.14+
node --version    # 18+
psql --version    # PostgreSQL 17
```

### Instalación Rápida

```bash
# 1. Backend
cd backend
poetry install
createdb booms_dev
poetry run alembic upgrade head
poetry run uvicorn app.main:app --port 8000

# 2. Frontend (en otra terminal)
cd frontend
npm install
npm run dev
```

**URLs:**
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173

## 📋 Los 7 Agentes Secuenciales

| # | Agente | Estado | Input | Output |
|---|--------|--------|-------|--------|
| 1 | **BOOMS** - Brand & Market Analysis | ✅ MVP | Conversación | Brand info, competidores, oportunidades |
| 2 | **Journey** - Customer Journey Mapping | ✅ MVP | Stage 1 + Conversación | Journey de 5 etapas con touchpoints |
| 3 | Agente de Ofertas 100M | 📋 Planeado | Stages 1-2 | Oferta irresistible |
| 4 | Selector de Canales | 📋 Planeado | Stages 1-3 | Matriz de canales |
| 5 | Atlas - AEO Strategist | 📋 Planeado | Stages 1-4 | Pilares de contenido |
| 6 | Planner - Content Strategist | 📋 Planeado | Stages 1-5 | Calendario 90 días |
| 7 | Agente de Budgets | 📋 Planeado | Stages 1-6 | Plan de medios |

### 🤖 Agentes Implementados

#### Agente 1: BOOMS (Brand Opportunity Optimization & Market Snapshot)
- **Modelo**: OpenAI GPT-4o
- **Función**: Análisis de marca, identificación de competidores, oportunidades de mercado
- **Output**: JSON con brand_name, industry, target_audience, competitors[], market_opportunities[]

#### Agente 2: Journey (Customer Journey Mapping)
- **Modelo**: Perplexity (con fallback a GPT-4o)
- **Función**: Mapeo del customer journey usando research actualizado
- **Output**: JSON con stages[] (Awareness, Consideration, Purchase, Retention, Advocacy)

## 🏗️ Arquitectura

```
booms-platform/
├── backend/                    # FastAPI + PostgreSQL
│   ├── app/
│   │   ├── agents/            # ✅ Agentes 1-2 (BOOMS, Journey)
│   │   ├── routers/           # ✅ Auth, Accounts, Stages, Agents, Exports
│   │   ├── models/            # ✅ User, Account, Stage (SQLAlchemy)
│   │   ├── schemas/           # ✅ Pydantic schemas
│   │   ├── services/          # ✅ OpenAI, Perplexity, PDF, Excel
│   │   └── utils/             # ✅ JWT, password hashing
│   ├── alembic/               # ✅ Migraciones DB
│   └── tests/                 # 📋 Tests pendientes
│
└── frontend/                   # React + TypeScript + Vite
    └── src/
        ├── components/         # ✅ Navbar, Loading, Modal
        ├── pages/             # ✅ Login, Dashboard, Chat
        ├── context/           # ✅ Auth Context
        ├── services/          # ✅ API Client (Axios)
        └── types/             # ✅ TypeScript definitions
```

### 🗄️ Base de Datos

```sql
users (id, email, hashed_password, full_name, timestamps)
  ↓ CASCADE DELETE
accounts (id, user_id, client_name, company_website, ai_model, timestamps)
  ↓ CASCADE DELETE
stages (id, account_id, stage_number[1-7], status, state[JSONB], output[JSONB], timestamps)

CONSTRAINTS:
- UNIQUE (account_id, stage_number)
- CHECK status IN ('locked', 'in_progress', 'completed')
- CHECK stage_number BETWEEN 1 AND 7
```

## 🔐 Arquitectura STATELESS

Cada agente NO tiene memoria entre mensajes:

1. **Frontend** → Envía mensaje + state actual
2. **Backend** → Construye prompt con contexto de stages anteriores
3. **AI Model** → Procesa y responde (GPT-4o o Perplexity)
4. **Backend** → Detecta completitud por JSON output
5. **Frontend** → Actualiza UI y desbloquea siguiente stage

**Estado completo en JSONB:**
- `state` column: Historial de conversación completo
- `output` column: Resultado final estructurado (JSON)

## 📡 API Endpoints

### Autenticación
```bash
POST   /auth/register     # Registro de usuario
POST   /auth/login        # Login (retorna JWT)
GET    /auth/me           # Info del usuario actual
```

### Cuentas (Accounts)
```bash
GET    /accounts          # Lista de cuentas
POST   /accounts          # Crear cuenta (auto-crea 7 stages)
GET    /accounts/{id}     # Detalle de cuenta
PATCH  /accounts/{id}     # Actualizar cuenta
DELETE /accounts/{id}     # Eliminar cuenta
```

### Stages
```bash
GET    /accounts/{id}/stages              # Lista stages de una cuenta
GET    /accounts/{id}/stages/{num}        # Detalle de stage específico
PATCH  /accounts/{id}/stages/{num}        # Actualizar stage
```

### Agentes AI
```bash
GET    /agents/accounts/{id}/stages/{num}/init  # Mensaje inicial del agente
POST   /agents/accounts/{id}/stages/{num}/chat  # Enviar mensaje al agente
```

### Exportación
```bash
GET    /exports/accounts/{id}/pdf     # Descargar reporte PDF
GET    /exports/accounts/{id}/excel   # Descargar reporte Excel
```

## 💻 Desarrollo

### Backend

```bash
cd backend

# Crear migración
poetry run alembic revision --autogenerate -m "Description"

# Aplicar migraciones
poetry run alembic upgrade head

# Ejecutar servidor
poetry run uvicorn app.main:app --reload --port 8000

# Tests (cuando se implementen)
poetry run pytest
```

### Frontend

```bash
cd frontend

# Desarrollo
npm run dev

# Build producción
npm run build

# Preview build
npm run preview
```

## 🎨 Stack Tecnológico

### Backend
- **FastAPI** - Framework web async
- **PostgreSQL** - Base de datos con soporte JSONB
- **SQLAlchemy 2.0** - ORM async
- **Alembic** - Migraciones
- **OpenAI API** - GPT-4o para Agente 1
- **Perplexity API** - Research para Agente 2
- **WeasyPrint** - Generación de PDFs
- **openpyxl** - Generación de Excel
- **Pydantic** - Validación de datos
- **Poetry** - Gestión de dependencias

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool moderno
- **React Router** - Navegación
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first styling
- **Lucide React** - Iconos

## 📊 Estado del Proyecto

### Completado ✅
- [x] Sistema de autenticación (JWT)
- [x] Gestión de usuarios
- [x] CRUD de cuentas (accounts)
- [x] Sistema de stages con desbloqueo secuencial
- [x] Agente 1: BOOMS (Brand & Market Analysis)
- [x] Agente 2: Journey (Customer Journey Mapping)
- [x] Exportación a PDF
- [x] Exportación a Excel
- [x] Frontend React completo
- [x] Dashboard y gestión de cuentas
- [x] Interfaz de chat con agentes
- [x] Integración full-stack MVP

### En Progreso 🚧
- [ ] Tests unitarios y de integración
- [ ] Agentes 3-7
- [ ] Sistema RAG con vectorstore

### Planeado 📋
- [ ] Tools/Function calling (Google Search)
- [ ] Edición de stages completados (con invalidación)
- [ ] Templates de prompts configurables
- [ ] Analytics y métricas
- [ ] Colaboración en equipo
- [ ] Notificaciones por email
- [ ] Webhooks para integraciones

## 🚢 Despliegue

### Recomendaciones de Hosting

**Backend:**
- Railway (recomendado) - PostgreSQL + FastAPI juntos
- Render - Free tier disponible
- Fly.io - Global deployment
- AWS ECS / Google Cloud Run

**Frontend:**
- Vercel (recomendado) - Deploy automático desde Git
- Netlify - Continuous deployment
- AWS S3 + CloudFront
- Google Firebase Hosting

**Database:**
- Railway PostgreSQL (recomendado)
- Supabase
- AWS RDS
- Google Cloud SQL

### Variables de Entorno - Producción

```bash
# Backend .env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
JWT_SECRET=<secure-random-string>
OPENAI_API_KEY=sk-...
PERPLEXITY_API_KEY=pplx-...
CORS_ORIGINS=["https://yourdomain.com"]
DEBUG_MODE=false
```

## 🛠️ Troubleshooting

### Backend no arranca

```bash
# Verificar PostgreSQL
pg_isready

# Recrear DB
dropdb booms_dev && createdb booms_dev
poetry run alembic upgrade head

# Reinstalar dependencias
poetry install
```

### Frontend no conecta al backend

1. Verificar que backend esté en http://localhost:8000
2. Revisar CORS en `backend/app/config.py`
3. Verificar `frontend/src/services/api.ts` tenga la URL correcta

### Errores de WeasyPrint (PDF)

```bash
# macOS - Instalar dependencias del sistema
brew install pango cairo glib gobject-introspection
```

## 📚 Documentación Adicional

- [Backend README](./backend/README.md) - Detalles del backend
- [Frontend README](./frontend/README.md) - Detalles del frontend
- [API Docs](http://localhost:8000/docs) - Swagger UI interactivo
- [Especificaciones](./spec/) - Ralph Wiggum specs originales

## 🤝 Contribución

Este es un proyecto propietario. Para desarrollo interno:

1. Crear branch desde `main`
2. Implementar feature
3. Asegurar que todo funciona
4. Submit PR para review

## 📝 Notas de Desarrollo

### Técnica Ralph Wiggum

Este proyecto fue desarrollado usando la metodología Ralph Wiggum:
- ✅ Especificaciones claras en `/spec`
- ✅ Implementación iterativa
- ✅ Validación continua
- ✅ MVP funcional primero, escalado después

### Próximos Pasos

1. **Implementar Tests** - Cobertura de código > 80%
2. **Agentes 3-4** - Ofertas y Canales
3. **Sistema RAG** - Vector DB con Langchain
4. **Optimizaciones** - Caching, rate limiting
5. **Deploy a Producción** - Railway + Vercel

## 📧 Soporte

Para issues técnicos o preguntas, contactar al equipo de desarrollo.

---

**Construido con ❤️ usando FastAPI, React, y OpenAI**

**MVP Status:** ✅ Completado y funcional
**Versión:** 0.1.0 (MVP con Agentes 1-2)
**Última actualización:** Enero 2026
