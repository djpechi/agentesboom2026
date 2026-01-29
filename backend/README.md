# BOOMS Platform - Backend

Backend de la plataforma BOOMS construido con FastAPI y Python 3.11+.

## ✅ Setup Completado

- ✅ Poetry instalado y configurado
- ✅ Todas las dependencias instaladas
- ✅ Estructura de directorios creada
- ✅ Archivo .env creado (necesita API keys)
- ✅ Base de datos PostgreSQL lista (booms_dev)

## 🔑 Configurar API Keys

Necesitas editar el archivo `.env` y agregar tus API keys:

### 1. OpenAI (Obligatorio)

1. Ve a: https://platform.openai.com/api-keys
2. Crea una nueva API key
3. Copia la key y pégala en `.env`:
   ```
   OPENAI_API_KEY=sk-tu-api-key-aqui
   ```

### 2. Perplexity (Opcional para Agente 2)

1. Ve a: https://www.perplexity.ai/settings/api
2. Crea cuenta y obtén API key
3. Copia la key y pégala en `.env`:
   ```
   PERPLEXITY_API_KEY=pplx-tu-api-key-aqui
   ```

## 🚀 Cómo Ejecutar

```bash
# 1. Activar entorno virtual de Poetry
poetry shell

# 2. Ejecutar servidor de desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Abrir documentación automática
# http://localhost:8000/docs
```

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── models/          # Modelos SQLAlchemy
│   ├── schemas/         # Schemas Pydantic
│   ├── routers/         # Endpoints de API
│   ├── services/        # Lógica de negocio
│   ├── tools/           # Herramientas (Perplexity, RAG)
│   ├── templates/pdf/   # Templates HTML para PDFs
│   ├── utils/           # Utilidades
│   ├── main.py          # Aplicación FastAPI
│   ├── config.py        # Configuración
│   ├── database.py      # Setup de DB
│   └── dependencies.py  # Dependencias de FastAPI
├── alembic/             # Migraciones de base de datos
├── data/pdfs/           # PDFs para RAG
├── tests/               # Tests
├── .env                 # Variables de entorno (NO versionar)
├── .env.example         # Ejemplo de .env
└── pyproject.toml       # Dependencias de Poetry
```

## 🗄️ Base de Datos

La base de datos `booms_dev` ya está creada.

Para crear las tablas:

```bash
# Inicializar Alembic (próximo paso)
poetry run alembic init alembic

# Crear primera migración
poetry run alembic revision --autogenerate -m "Initial migration"

# Ejecutar migraciones
poetry run alembic upgrade head
```

## 📦 Dependencias Instaladas

### Core
- FastAPI 0.128.0
- Uvicorn 0.40.0
- SQLAlchemy 2.0.46 (async)
- Alembic 1.18.1
- asyncpg 0.31.0

### Auth
- python-jose[cryptography] 3.5.0
- passlib[bcrypt] 1.7.4
- pydantic-settings 2.12.0

### AI
- openai 2.15.0
- httpx 0.28.1 (para Perplexity)

### Exportación
- weasyprint 68.0 (PDF)
- openpyxl 3.1.5 (Excel)
- jinja2 3.1.6 (Templates)

### Dev
- pytest 9.0.2
- pytest-asyncio 1.3.0
- black 26.1.0
- ruff 0.14.14

## 🎯 Próximos Pasos

Ver: `/docs/mvp-implementation-plan.md`

**Fase 1**: ✅ Completada - Backend setup
**Fase 2**: Crear modelos de base de datos y migraciones
**Fase 3**: Implementar sistema de autenticación
**Fase 4**: Gestión de cuentas
**Fase 5**: Implementar Agentes 1 y 2

## 🧪 Ejecutar Tests

```bash
poetry run pytest
```

## 🔍 Linting y Formateo

```bash
# Formatear código
poetry run black .

# Linting
poetry run ruff check .
```
