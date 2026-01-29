# Próximos Pasos - BOOMS Platform (Actualizado con FastAPI)

## ✅ Stack Tecnológico ACTUALIZADO

### Backend: FastAPI (Python 3.11+)

**Por qué FastAPI es mejor para BOOMS:**

1. ✅ **Python Nativo** - Todas las librerías de IA son de Python
2. ✅ **Async/Await** - Perfecto para llamadas a APIs de IA
3. ✅ **Ecosistema de IA** - Langchain, embeddings, RAG todo en Python
4. ✅ **Auto-documentación** - Swagger UI automático
5. ✅ **Perplexity Integration** - httpx async para búsquedas
6. ✅ **Type Safety** - Pydantic para validación

### Stack Completo

```
Frontend:  React + TypeScript + Tailwind + shadcn/ui
Backend:   FastAPI + Python 3.11+
Database:  PostgreSQL + SQLAlchemy + Alembic
Auth:      JWT (python-jose) + bcrypt (passlib)
AI:        OpenAI, Anthropic, Google (SDKs nativos de Python)
Tools:     Perplexity Search (httpx async)
RAG:       Langchain + sentence-transformers + pgvector
Exports:   ReportLab/WeasyPrint (PDF) + openpyxl (Excel)
```

---

## 🚀 Setup Inicial (Opción 1: Manual)

### 1. Preparar Entorno

```bash
# 1. Instalar PostgreSQL (si no está instalado)
# macOS:
brew install postgresql@15
brew services start postgresql@15

# Linux:
sudo apt-get install postgresql-15

# 2. Crear base de datos
createdb booms_dev

# 3. Instalar Python 3.11+
# macOS:
brew install python@3.11

# Linux (usando pyenv - recomendado):
pyenv install 3.11.7
pyenv local 3.11.7

# 4. Instalar Poetry (gestor de dependencias Python)
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Inicializar Proyecto Backend (FastAPI)

```bash
cd booms-platform
mkdir backend && cd backend

# Inicializar Poetry
poetry init -n

# Configurar Python 3.11
poetry env use python3.11

# Instalar dependencias core
poetry add fastapi uvicorn[standard]
poetry add "sqlalchemy[asyncio]" alembic asyncpg
poetry add "pydantic[email]" pydantic-settings
poetry add python-jose[cryptography] passlib[bcrypt]
poetry add httpx python-multipart

# AI SDKs
poetry add openai anthropic google-generativeai

# RAG & Embeddings
poetry add langchain sentence-transformers pypdf

# PDF/Excel Generation
poetry add reportlab weasyprint openpyxl

# Dev dependencies
poetry add --group dev pytest pytest-asyncio black ruff

# Crear estructura de carpetas
mkdir -p app/{models,schemas,routers,services,tools,prompts,utils}
mkdir -p app/models app/schemas app/routers app/services app/tools app/prompts app/utils
mkdir -p alembic/versions
mkdir -p data/pdfs
mkdir -p tests

# Crear archivos iniciales
touch app/__init__.py
touch app/main.py
touch app/config.py
touch app/database.py
touch app/dependencies.py

# Crear .env
cat > .env << EOF
# Database
DATABASE_URL=postgresql://localhost:5432/booms_dev

# JWT
JWT_SECRET=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

# AI Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=AIza...
PERPLEXITY_API_KEY=pplx-...

# Default Model
DEFAULT_AI_MODEL=openai-gpt4o

# CORS
CORS_ORIGINS=["http://localhost:5173"]
EOF

# Copiar .env.example
cp .env .env.example
# Editar .env.example para remover valores sensibles
```

### 3. Configurar Alembic (Migraciones)

```bash
# Inicializar Alembic
poetry run alembic init alembic

# Editar alembic.ini - actualizar sqlalchemy.url
# Comentar la línea: sqlalchemy.url = ...

# Editar alembic/env.py
```

```python
# alembic/env.py
from app.database import Base
from app.config import get_settings
from app.models import user, account, stage, conversation

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata
```

### 4. Crear Primera Migración

```bash
# Crear modelos SQLAlchemy en app/models/
# (user.py, account.py, stage.py, conversation.py)

# Generar migración inicial
poetry run alembic revision --autogenerate -m "Initial migration"

# Revisar migración generada en alembic/versions/

# Ejecutar migración
poetry run alembic upgrade head
```

### 5. Ejecutar Servidor

```bash
# Activar entorno virtual
poetry shell

# Ejecutar con reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API estará en: http://localhost:8000
# Docs automáticos: http://localhost:8000/docs
```

### 6. Inicializar Proyecto Frontend (React)

```bash
cd ..
npm create vite@latest frontend -- --template react-ts
cd frontend

# Instalar dependencias
npm install react-router-dom axios
npm install -D tailwindcss postcss autoprefixer
npm install lucide-react

# Configurar Tailwind
npx tailwindcss init -p

# Instalar shadcn/ui
npx shadcn-ui@latest init

# Crear estructura de carpetas
mkdir -p src/components/{ui,layout,auth,dashboard,pipeline,chat,output,settings}
mkdir -p src/pages src/contexts src/hooks src/services src/types src/utils

# Crear .env
cat > .env << EOF
VITE_API_URL=http://localhost:8000/api
EOF

# Ejecutar frontend
npm run dev
```

---

## 📁 Estructura de Archivos Creados

```
booms-platform/
├── spec/                          # ✅ Especificaciones completas
│   ├── jtbd/                     # 5 documentos
│   ├── topics/                   # 14 especificaciones técnicas
│   │   ├── 01-database-schema.md
│   │   ├── 02-authentication.md
│   │   ├── 03-ai-agents-system.md
│   │   ├── 04-ai-provider-service.md
│   │   ├── 05-frontend-architecture.md
│   │   ├── 06-api-endpoints.md
│   │   ├── 07-export-system.md (PDF/Excel con FastAPI)
│   │   ├── 08-tools-system.md (Perplexity)
│   │   ├── 09-rag-system.md
│   │   ├── 10-account-context-passing.md
│   │   ├── 11-perplexity-vs-google.md
│   │   ├── 12-backend-fastapi-architecture.md
│   │   ├── 13-progress-persistence-sequential-flow.md
│   │   └── 14-demo-autochat-system.md ← NUEVO
│   └── prompts/
│       ├── agent-1-booms.md         # ✅ Adaptado
│       ├── agent-2-journey.md       # ✅ Adaptado
│       └── AGENTS_CAPABILITIES.md   # ✅ Referencia completa de todos los agentes
│
├── docs/
│   └── implementation-plan.md    # ✅ Actualizado para FastAPI
│
├── backend/                       # Crear manualmente
│   ├── app/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   └── main.py
│   ├── alembic/
│   ├── .env
│   └── pyproject.toml
│
└── frontend/                      # Crear con Vite
    ├── src/
    └── package.json
```

---

## 🔧 APIs y Claves Necesarias

### Obligatorias

1. **OpenAI**: https://platform.openai.com/api-keys
   - Modelo: GPT-4o
   - Costo: ~$0.01 por 1K tokens

2. **PostgreSQL**: Local o servicio cloud
   - Supabase (gratis): https://supabase.com
   - Railway (gratis con límite): https://railway.app

### Opcionales (pero recomendadas)

3. **Perplexity**: https://www.perplexity.ai/settings/api
   - $5 de crédito gratis
   - $0.001 por búsqueda (sonar)
   - Altamente recomendado para agentes 2-7

4. **Anthropic Claude**: https://console.anthropic.com/
   - Alternativa a OpenAI
   - Mejor para razonamiento complejo

5. **Google AI Studio**: https://aistudio.google.com/app/apikey
   - Alternativa a OpenAI
   - Gemini 2.5 Pro

---

## 📊 Ventajas de FastAPI sobre Node.js

| Aspecto | Node.js + Express | FastAPI + Python |
|---------|-------------------|------------------|
| **AI SDKs** | Wrappers de Python | Nativos ✅ |
| **Async** | Callbacks/Promises | async/await nativo ✅ |
| **RAG/Embeddings** | Limitado | Ecosistema completo ✅ |
| **Perplexity** | Wrapper manual | httpx async ✅ |
| **Type Safety** | TypeScript (separado) | Pydantic integrado ✅ |
| **Auto-docs** | Manual | Swagger automático ✅ |
| **PDF/Vector DB** | Librerías limitadas | Nativo de Python ✅ |

---

## 🎯 Estimación Actualizada

- **Tiempo**: 25-35 días (sin cambios)
- **Ventaja**: Desarrollo más rápido con FastAPI para features de IA
- **Costo APIs**: ~$10-20/mes en desarrollo

---

## 📝 Agentes Adaptados Hasta Ahora

1. ✅ **Agente 1: Booms** (Buyer Persona)
   - 27-28 preguntas
   - Tools: RAG (documentos Scaling Up, conceptos verde/superverde)
   - Output: Buyer Persona + Scaling Up Table

2. ✅ **Agente 2: Journey** (Buyer's Journey)
   - 12-16 preguntas
   - Tools: Perplexity Search
   - Input: Output del Agente 1
   - Output: Journey Table + Narrative + HubSpot Recommendations

3. ⏳ **Agente 3: Ofertas 100M** (próximo)
   - Tools: Perplexity Search + RAG (Hormozi, StoryBrand)
   - Input: Outputs de Agentes 1 y 2

---

## 🚀 Siguiente Paso: Implementar MVP

### ✅ Estado Actual

**Especificaciones**: 14/14 completas ✅
- Todos los JTBD documentados
- Toda la arquitectura especificada
- 2 agentes adaptados (Booms + Journey)
- Sistema de exportación definido
- Demo autochat especificado

**Decisión**: Implementar MVP con Agentes 1-2 primero, validar arquitectura, luego escalar a agentes 3-7.

### 📋 Plan de Implementación MVP

Consulta el plan detallado en: **`/docs/mvp-implementation-plan.md`**

**Resumen del MVP**:
- ✅ Backend FastAPI completo
- ✅ PostgreSQL + Alembic
- ✅ Auth JWT
- ✅ Agente 1: Booms (100% funcional)
- ✅ Agente 2: Journey (100% funcional)
- ✅ Exportación PDF/Excel
- ✅ Demo Autochat
- ✅ Frontend React completo

**Tiempo estimado**: ~15 días (3 semanas)

### 🎯 Fases de Implementación

| Fase | Descripción | Duración |
|------|-------------|----------|
| 0 | Setup Entorno | 1 día |
| 1 | Backend Setup (FastAPI + Poetry) | 1 día |
| 2 | Database (Modelos + Migraciones) | 1 día |
| 3 | Auth System (JWT) | 1 día |
| 4 | Gestión de Cuentas | 0.5 días |
| 5 | **Agentes 1-2** (Core!) | 2-3 días |
| 6 | Exportación PDF/Excel | 1 día |
| 7 | Demo Autochat | 1 día |
| 8 | Frontend React | 3-4 días |
| 9 | Testing y Refinamiento | 2 días |

### 🚦 Primer Paso: Fase 0 (Setup)

```bash
# 1. Instalar PostgreSQL
brew install postgresql@15
brew services start postgresql@15
createdb booms_dev

# 2. Instalar Python 3.11 y Poetry
brew install python@3.11
curl -sSL https://install.python-poetry.org | python3 -

# 3. Obtener API Keys
# - OpenAI: https://platform.openai.com/api-keys
# - (Opcional) Perplexity: https://www.perplexity.ai/settings/api
```

Ver **pasos detallados** en `/docs/mvp-implementation-plan.md`

### 📊 Después del MVP

Una vez validado el MVP (Agentes 1-2):
1. Adaptar prompts de Agentes 3-7
2. Implementar agentes restantes
3. Agregar RAG system
4. Deploy a producción

---

## 💡 Ventajas de Este Enfoque

✅ **Validación temprana** - Probar arquitectura con 2 agentes reales
✅ **Feedback rápido** - Ver el sistema funcionando en 3 semanas
✅ **Iteración** - Ajustar antes de escalar a 7 agentes
✅ **Aprendizaje** - Entender bien el flujo antes de replicar
✅ **Demo funcional** - Mostrar a stakeholders progreso real
