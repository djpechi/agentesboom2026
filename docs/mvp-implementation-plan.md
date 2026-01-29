# Plan de Implementación MVP - BOOMS Platform

## Objetivo

Implementar un MVP funcional con **Agentes 1 y 2** para validar la arquitectura antes de escalar a los 7 agentes.

## Alcance del MVP

### ✅ Incluye

- ✅ **Backend FastAPI** completo
- ✅ **Base de datos PostgreSQL** con migraciones
- ✅ **Auth JWT** (registro, login)
- ✅ **Agente 1: Booms** (Buyer Persona) - 100% funcional
- ✅ **Agente 2: Journey** (Buyer's Journey) - 100% funcional
- ✅ **Exportación PDF/Excel** para Agentes 1 y 2
- ✅ **Demo Autochat** para testing rápido
- ✅ **Persistencia de progreso** (pausar/continuar)
- ✅ **Flujo secuencial** (1→2)
- ✅ **Frontend React** con UI completa

### ⏳ No Incluye (para después)

- Agentes 3-7 (se agregan después de validar MVP)
- RAG system (solo si Agente 1 lo necesita - verificar)
- Perplexity Search (Agente 2 lo usa)
- Multi-modelo AI (solo OpenAI por ahora)

## Fases de Implementación

---

## FASE 0: Setup del Entorno (1 día)

### 0.1 Instalar Dependencias del Sistema

```bash
# macOS
brew install postgresql@15
brew install python@3.11
brew install cairo pango gdk-pixbuf libffi  # Para WeasyPrint

# Iniciar PostgreSQL
brew services start postgresql@15

# Instalar Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

### 0.2 Crear Base de Datos

```bash
# Crear DB
createdb booms_dev

# Crear usuario (opcional)
psql booms_dev
# CREATE USER booms_user WITH PASSWORD 'password';
# GRANT ALL PRIVILEGES ON DATABASE booms_dev TO booms_user;
```

### 0.3 Obtener API Keys

```bash
# Necesario para el MVP:
1. OpenAI API Key: https://platform.openai.com/api-keys
   - Modelo: gpt-4o
   - Costo estimado: $5-10 para testing

2. (Opcional) Perplexity API Key: https://www.perplexity.ai/settings/api
   - Para Agente 2
   - $5 de crédito gratis
```

### Resultado Fase 0
- ✅ PostgreSQL corriendo
- ✅ Python 3.11 instalado
- ✅ Poetry instalado
- ✅ API keys obtenidas

---

## FASE 1: Backend - Setup Inicial (1 día)

### 1.1 Crear Proyecto Backend

```bash
cd booms-platform
mkdir backend
cd backend

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

# AI SDKs (solo OpenAI por ahora)
poetry add openai

# Para Perplexity (Agente 2)
# Ya incluido con httpx

# Exportación
poetry add weasyprint openpyxl jinja2

# Dev dependencies
poetry add --group dev pytest pytest-asyncio black ruff
```

### 1.2 Crear Estructura de Directorios

```bash
# Estructura completa
mkdir -p app/{models,schemas,routers,services,tools,templates,utils}
mkdir -p app/templates/pdf
mkdir -p alembic/versions
mkdir -p data/pdfs
mkdir -p tests

# Archivos iniciales
touch app/__init__.py
touch app/main.py
touch app/config.py
touch app/database.py
touch app/dependencies.py
```

### 1.3 Configurar .env

```bash
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql+asyncpg://localhost:5432/booms_dev

# JWT
JWT_SECRET=tu-secret-key-aqui-generar-con-openssl-rand-hex-32
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

# AI Providers
OPENAI_API_KEY=sk-...

# Perplexity (para Agente 2)
PERPLEXITY_API_KEY=pplx-...

# CORS
CORS_ORIGINS=["http://localhost:5173"]

# Demo Mode
DEBUG_MODE=true
EOF

# Generar JWT secret
echo "JWT_SECRET=$(openssl rand -hex 32)" >> .env
```

### 1.4 Crear app/config.py

```python
# /backend/app/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    database_url: str

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_days: int = 7

    # AI
    openai_api_key: str
    perplexity_api_key: str | None = None

    # CORS
    cors_origins: list[str] = ["http://localhost:5173"]

    # Debug
    debug_mode: bool = False

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
```

### 1.5 Crear app/database.py

```python
# /backend/app/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=True,  # Log SQL queries (dev only)
    future=True
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

### 1.6 Crear app/main.py

```python
# /backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="BOOMS Platform API",
    description="AI-powered marketing onboarding platform",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "BOOMS Platform API", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Routers se agregarán después
# from app.routers import auth, accounts, stages, agents, exports, demo
# app.include_router(auth.router)
# app.include_router(accounts.router)
# ...
```

### Resultado Fase 1
- ✅ Proyecto backend creado
- ✅ Dependencias instaladas
- ✅ Configuración lista
- ✅ FastAPI corriendo en http://localhost:8000

**Test**:
```bash
poetry shell
uvicorn app.main:app --reload
# Abrir http://localhost:8000/docs
```

---

## FASE 2: Database - Modelos y Migraciones (1 día)

### 2.1 Crear Modelos

```python
# /backend/app/models/user.py

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

```python
# /backend/app/models/account.py

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    client_name = Column(String(255), nullable=False)
    company_website = Column(String(500), nullable=True)
    ai_model = Column(String(50), nullable=False, default="openai-gpt4o")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="accounts")
    stages = relationship("Stage", back_populates="account", cascade="all, delete-orphan")
```

```python
# /backend/app/models/stage.py

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class Stage(Base):
    __tablename__ = "stages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    stage_number = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default="locked")  # locked, in_progress, completed
    state = Column(JSONB, default={})
    output = Column(JSONB, nullable=True)
    ai_model_used = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    account = relationship("Account", back_populates="stages")

    # Constraints
    __table_args__ = (
        UniqueConstraint('account_id', 'stage_number', name='uq_account_stage'),
    )
```

### 2.2 Configurar Alembic

```bash
# Inicializar Alembic
poetry run alembic init alembic
```

Editar `alembic.ini`:
```ini
# Comentar esta línea:
# sqlalchemy.url = driver://user:pass@localhost/dbname
```

Editar `alembic/env.py`:
```python
from app.database import Base
from app.config import get_settings
from app.models.user import User
from app.models.account import Account
from app.models.stage import Stage

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata
```

### 2.3 Crear Primera Migración

```bash
# Generar migración
poetry run alembic revision --autogenerate -m "Initial migration"

# Revisar archivo generado en alembic/versions/

# Ejecutar migración
poetry run alembic upgrade head
```

### 2.4 Verificar Base de Datos

```bash
psql booms_dev

\dt  # Listar tablas
# Deberías ver: users, accounts, stages, alembic_version

\d users  # Ver estructura de tabla users
```

### Resultado Fase 2
- ✅ 3 modelos creados (User, Account, Stage)
- ✅ Migración ejecutada
- ✅ Tablas creadas en PostgreSQL

---

## FASE 3: Auth System (1 día)

### 3.1 Schemas Pydantic

```python
# /backend/app/schemas/user.py

from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str | None
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

### 3.2 Auth Service

```python
# /backend/app/services/auth_service.py

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.jwt_expiration_days)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
```

### 3.3 Dependencies

```python
# /backend/app/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.services.auth_service import decode_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        payload = decode_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
```

### 3.4 Auth Router

```python
# /backend/app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Verificar si email existe
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Crear usuario
    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Generar token
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token}

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    # Buscar usuario
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generar token
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

### 3.5 Agregar Router a Main

```python
# /backend/app/main.py

from app.routers import auth

app.include_router(auth.router)
```

### Resultado Fase 3
- ✅ Sistema de auth completo
- ✅ Endpoints: /api/auth/register, /api/auth/login, /api/auth/me
- ✅ JWT funcionando

**Test**:
```bash
# Swagger UI: http://localhost:8000/docs
# Probar registro y login
```

---

## FASE 4: Gestión de Cuentas (0.5 días)

### 4.1 Schemas

```python
# /backend/app/schemas/account.py

from pydantic import BaseModel, HttpUrl
from datetime import datetime
from uuid import UUID

class AccountCreate(BaseModel):
    client_name: str
    company_website: str | None = None
    ai_model: str = "openai-gpt4o"

class AccountResponse(BaseModel):
    id: UUID
    client_name: str
    company_website: str | None
    ai_model: str
    created_at: datetime

    class Config:
        from_attributes = True
```

### 4.2 Account Router

```python
# /backend/app/routers/accounts.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.account import Account
from app.models.stage import Stage
from app.schemas.account import AccountCreate, AccountResponse

router = APIRouter(prefix="/api/accounts", tags=["accounts"])

@router.post("", response_model=AccountResponse)
async def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Crear cuenta
    account = Account(
        user_id=current_user.id,
        **account_data.model_dump()
    )
    db.add(account)
    await db.flush()

    # Crear 7 stages (solo 2 por ahora para MVP)
    for stage_num in range(1, 3):  # Solo agentes 1 y 2
        stage = Stage(
            account_id=account.id,
            stage_number=stage_num,
            status="in_progress" if stage_num == 1 else "locked"
        )
        db.add(stage)

    await db.commit()
    await db.refresh(account)

    return account

@router.get("", response_model=list[AccountResponse])
async def list_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Account).where(Account.user_id == current_user.id)
    )
    return result.scalars().all()

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    account = await db.get(Account, account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")
    return account
```

### 4.3 Agregar a Main

```python
from app.routers import auth, accounts

app.include_router(accounts.router)
```

### Resultado Fase 4
- ✅ CRUD de cuentas
- ✅ Crear cuenta inicializa stages 1-2

---

## FASE 5: Agentes 1 y 2 - Implementación Core (2-3 días)

Esta es la fase más importante. Aquí implementamos los 2 agentes funcionales.

### 5.1 AI Provider Service

```python
# /backend/app/services/ai_provider_service.py

from openai import AsyncOpenAI
from app.config import get_settings

settings = get_settings()

class AIProviderService:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def chat_with_agent(
        self,
        stage_number: int,
        user_message: str,
        context: dict
    ) -> dict:
        """
        Ejecuta conversación con un agente específico

        Returns JSON con formato STATELESS:
        {
            "agentMessage": "...",
            "updatedState": {...},
            "progress": 50,
            "isComplete": false,
            "output": null
        }
        """
        # Cargar prompt del agente
        from app.services.agent_prompts import get_agent_prompt

        system_prompt = get_agent_prompt(stage_number, context)

        # Llamar a OpenAI
        response = await self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message or "Comenzar"}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )

        # Parsear respuesta JSON
        import json
        return json.loads(response.choices[0].message.content)
```

### 5.2 Agent Prompts

Crear archivos con los prompts de los agentes 1 y 2 que ya tenemos especificados.

```python
# /backend/app/services/agent_prompts.py

def get_agent_prompt(stage_number: int, context: dict) -> str:
    if stage_number == 1:
        return get_agent_1_prompt(context)
    elif stage_number == 2:
        return get_agent_2_prompt(context)
    else:
        raise ValueError(f"Agent {stage_number} not implemented yet")

def get_agent_1_prompt(context: dict) -> str:
    """Prompt del Agente 1: Booms"""
    # Aquí va el prompt completo del archivo agent-1-booms.md
    # Adaptado para incluir el contexto
    return f"""
    [Prompt completo del Agente 1 aquí...]

    Contexto de la cuenta:
    - Consultor: {context['accountContext']['consultantName']}
    - Cliente: {context['accountContext']['companyName']}
    - Website: {context['accountContext']['companyWebsite']}

    Estado previo: {context.get('currentState', {{}})}

    [Resto del prompt...]
    """

def get_agent_2_prompt(context: dict) -> str:
    """Prompt del Agente 2: Journey"""
    # Aquí va el prompt del agent-2-journey.md
    # Incluye output del Agente 1
    return f"""
    [Prompt completo del Agente 2...]

    Output del Agente 1:
    {context.get('previousAgentOutputs', {}).get('agent1Output', {})}

    [Resto del prompt...]
    """
```

### 5.3 Agents Router

```python
# /backend/app/routers/agents.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.stage import Stage
from app.models.account import Account
from app.services.ai_provider_service import AIProviderService

router = APIRouter(prefix="/api/agents", tags=["agents"])
ai_service = AIProviderService()

class ChatMessage(BaseModel):
    content: str

@router.post("/stages/{stage_id}/chat")
async def chat_with_agent(
    stage_id: str,
    message: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Obtener stage
    stage = await db.get(Stage, stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")

    # Verificar ownership
    account = await db.get(Account, stage.account_id)
    if account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Construir contexto
    context = {
        "accountContext": {
            "consultantName": current_user.full_name or "Consultor",
            "companyName": account.client_name,
            "companyWebsite": account.company_website
        },
        "currentState": stage.state or {},
        "previousAgentOutputs": await _get_previous_outputs(stage, db)
    }

    # Ejecutar agente
    response = await ai_service.chat_with_agent(
        stage_number=stage.stage_number,
        user_message=message.content,
        context=context
    )

    # Guardar estado
    stage.state = response["updatedState"]

    # Si completó, guardar output
    if response.get("isComplete"):
        stage.status = "completed"
        stage.output = response["output"]
        stage.completed_at = datetime.utcnow()

        # Desbloquear siguiente stage
        await _unlock_next_stage(stage, db)

    await db.commit()

    return response

async def _get_previous_outputs(stage: Stage, db: AsyncSession) -> dict:
    # Implementar según spec/topics/13
    ...

async def _unlock_next_stage(stage: Stage, db: AsyncSession):
    # Implementar según spec/topics/13
    ...
```

### Resultado Fase 5
- ✅ Agente 1 funcional
- ✅ Agente 2 funcional
- ✅ Flujo de conversación completo
- ✅ Persistencia de progreso
- ✅ Desbloqueo secuencial

---

## FASE 6: Exportación PDF/Excel (1 día)

Implementar según `/spec/topics/07-export-system.md`

---

## FASE 7: Demo Autochat (1 día)

Implementar según `/spec/topics/14-demo-autochat-system.md`

---

## FASE 8: Frontend React (3-4 días)

### 8.1 Setup

```bash
cd ..  # Volver a booms-platform/
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install

# Dependencias
npm install react-router-dom axios
npm install -D tailwindcss postcss autoprefixer
npm install lucide-react

# shadcn/ui
npx shadcn-ui@latest init
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
```

### 8.2 Implementar Páginas

1. Login/Register
2. Dashboard (lista de cuentas)
3. Account Detail (pipeline visual)
4. Agent Chat (interfaz genérica)
5. Output View (con botones de descarga)

---

## FASE 9: Testing y Refinamiento (2 días)

- Probar flujo completo 1→2
- Verificar exportación PDF/Excel
- Probar demo autochat
- Ajustar prompts según resultados

---

## Cronograma Estimado

| Fase | Duración | Total Acumulado |
|------|----------|-----------------|
| 0. Setup Entorno | 1 día | 1 día |
| 1. Backend Setup | 1 día | 2 días |
| 2. Database | 1 día | 3 días |
| 3. Auth | 1 día | 4 días |
| 4. Accounts | 0.5 días | 4.5 días |
| 5. Agentes 1-2 | 2-3 días | 7 días |
| 6. Exportación | 1 día | 8 días |
| 7. Demo Autochat | 1 día | 9 días |
| 8. Frontend | 3-4 días | 13 días |
| 9. Testing | 2 días | 15 días |

**Total: ~15 días (3 semanas) para MVP funcional**

---

## Checklist de Validación del MVP

### ✅ Backend
- [ ] FastAPI corriendo en localhost:8000
- [ ] Swagger docs en /docs funcionando
- [ ] Registro de usuario funcional
- [ ] Login retorna JWT válido
- [ ] Crear cuenta funciona
- [ ] Agente 1 responde preguntas
- [ ] Agente 1 completa y genera output
- [ ] Agente 2 se desbloquea automáticamente
- [ ] Agente 2 recibe output de Agente 1
- [ ] Agente 2 completa y genera output
- [ ] PDF se genera correctamente
- [ ] Excel se genera correctamente
- [ ] Demo autochat completa Agente 1
- [ ] Demo autochat completa Agente 2
- [ ] Progreso se guarda en cada pregunta
- [ ] Pausar y continuar funciona

### ✅ Frontend
- [ ] Login UI funcional
- [ ] Dashboard muestra cuentas
- [ ] Crear nueva cuenta funciona
- [ ] Pipeline muestra estados (locked/in_progress/completed)
- [ ] Chat con Agente 1 funciona
- [ ] Progreso visual se actualiza
- [ ] Completar Agente 1 muestra output
- [ ] Botones de descarga (PDF/Excel) funcionan
- [ ] Agente 2 se desbloquea visualmente
- [ ] Chat con Agente 2 funciona
- [ ] Botón "Demo Auto" visible (dev mode)
- [ ] Demo autochat muestra log en tiempo real

---

## Siguiente Paso Después del MVP

Una vez que el MVP esté funcionando:

1. **Adaptar Agentes 3-7** - Obtener prompts de Relevance
2. **Agregar Perplexity** a más agentes
3. **Implementar RAG** si es necesario
4. **Multi-modelo** (Anthropic, Google)
5. **Deployment** a producción

---

## ¿Empezamos con la Fase 0?

Puedo ayudarte paso a paso con cada fase. ¿Quieres que empecemos con el setup del entorno?
