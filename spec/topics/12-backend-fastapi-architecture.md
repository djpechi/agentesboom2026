# Especificación: Arquitectura Backend con FastAPI

## Stack Tecnológico Backend

- **Framework**: FastAPI
- **Lenguaje**: Python 3.11+
- **ORM**: SQLAlchemy 2.0
- **Migraciones**: Alembic
- **Validación**: Pydantic v2
- **Auth**: python-jose (JWT) + passlib (bcrypt)
- **Database**: PostgreSQL (asyncpg driver)
- **HTTP Client**: httpx (async)
- **CORS**: fastapi.middleware.cors

## Por Qué FastAPI

### Ventajas para BOOMS

1. **Python Nativo**
   - OpenAI SDK es de Python
   - Anthropic SDK es de Python
   - Google AI SDK es de Python
   - Perplexity API funciona perfecto con httpx
   - Sin wrappers ni adaptadores

2. **Async/Await**
   - Llamadas a APIs de IA son naturalmente async
   - Mejor performance para operaciones I/O bound
   - Manejo de múltiples requests simultáneos

3. **Ecosistema de IA**
   - Langchain para RAG
   - sentence-transformers para embeddings
   - pgvector con SQLAlchemy
   - PDF parsing con pypdf
   - Todo el ecosistema de ML/IA

4. **Auto-documentación**
   - OpenAPI/Swagger automático
   - Schemas de Pydantic → Swagger UI
   - Fácil de testear endpoints

5. **Type Safety**
   - Pydantic para validación
   - Type hints de Python
   - Errores en desarrollo, no en producción

## Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app
│   ├── config.py                  # Settings con pydantic-settings
│   ├── database.py                # Database connection
│   ├── dependencies.py            # Dependency injection
│   │
│   ├── models/                    # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── account.py
│   │   ├── stage.py
│   │   └── conversation.py
│   │
│   ├── schemas/                   # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── account.py
│   │   ├── stage.py
│   │   └── chat.py
│   │
│   ├── routers/                   # API routers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── accounts.py
│   │   ├── stages.py
│   │   ├── agents.py
│   │   └── exports.py
│   │
│   ├── services/                  # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── ai_provider.py        # Multi-model AI
│   │   ├── context_builder.py
│   │   ├── perplexity_search.py
│   │   ├── rag_service.py
│   │   └── export_service.py
│   │
│   ├── tools/                     # Agent tools
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── perplexity.py
│   │   └── calculator.py
│   │
│   ├── prompts/                   # Agent prompts
│   │   ├── agent_1_system.txt
│   │   ├── agent_2_system.txt
│   │   └── ...
│   │
│   └── utils/                     # Utilities
│       ├── __init__.py
│       ├── security.py
│       └── pdf_generator.py
│
├── alembic/                       # Database migrations
│   ├── versions/
│   └── env.py
│
├── data/                          # RAG documents
│   └── pdfs/
│       ├── agent-1/
│       ├── agent-3/
│       └── ...
│
├── tests/
│   ├── test_auth.py
│   ├── test_agents.py
│   └── ...
│
├── .env
├── .env.example
├── alembic.ini
├── pyproject.toml                 # Poetry dependencies
└── README.md
```

## Configuración (config.py)

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    app_name: str = "BOOMS Platform"
    debug: bool = False

    # Database
    database_url: str

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_days: int = 7

    # AI Providers
    openai_api_key: str
    anthropic_api_key: str | None = None
    google_ai_api_key: str | None = None
    perplexity_api_key: str | None = None

    # Default AI Model
    default_ai_model: str = "openai-gpt4o"

    # CORS
    cors_origins: list[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
```

## Database Setup (database.py)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import get_settings

settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.debug,
    future=True
)

# Create async session factory
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Dependency
async def get_db():
    async with async_session_maker() as session:
        yield session
```

## Main App (main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import auth, accounts, stages, agents, exports

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Plataforma de Onboarding de Marketing con 7 Agentes de IA",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
app.include_router(stages.router, prefix="/api/stages", tags=["stages"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(exports.router, prefix="/api/exports", tags=["exports"])

@app.get("/")
async def root():
    return {"message": "BOOMS Platform API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

## Models (SQLAlchemy)

### models/user.py

```python
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### models/account.py

```python
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    client_name = Column(String(255), nullable=False)
    company_website = Column(String(500), nullable=True)
    ai_model = Column(String(50), nullable=False, default="openai-gpt4o")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="accounts")
    stages = relationship("Stage", back_populates="account", cascade="all, delete-orphan")
```

## Schemas (Pydantic)

### schemas/auth.py

```python
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    user_id: UUID
    email: str
```

### schemas/chat.py

```python
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Any, Optional

class ChatRequest(BaseModel):
    account_id: UUID
    stage_id: UUID
    stage_number: int = Field(..., ge=1, le=7)
    user_message: str
    conversation_state: Optional[dict[str, Any]] = None

class ChatResponse(BaseModel):
    agent_message: str
    updated_state: dict[str, Any]
    progress: int = Field(..., ge=0, le=100)
    is_complete: bool
    output: Optional[dict[str, Any]] = None
    metadata: Optional[dict[str, Any]] = None
```

## Routers

### routers/auth.py

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth import UserCreate, UserLogin, TokenResponse, UserResponse
from app.services.auth_service import AuthService
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    auth_service = AuthService(db)
    return await auth_service.register(user_data)

@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login user"""
    auth_service = AuthService(db)
    return await auth_service.login(credentials)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user info"""
    return current_user
```

### routers/agents.py

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_provider import AIProviderService
from app.services.context_builder import ContextBuilder
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to an AI agent and get response.

    The agent is stateless - all context is passed in the request.
    """
    # Verify account ownership
    # ... (check that account belongs to current_user)

    # Build context
    context_builder = ContextBuilder(db)
    context = await context_builder.build_context(
        account_id=request.account_id,
        stage_number=request.stage_number,
        conversation_state=request.conversation_state
    )

    # Get AI provider
    ai_provider = AIProviderService()

    # Chat with agent
    response = await ai_provider.chat_with_agent(
        stage_number=request.stage_number,
        user_message=request.user_message,
        context=context
    )

    # Save to database
    # ... (save conversation history, update stage state)

    return response
```

## Services

### services/ai_provider.py

```python
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import google.generativeai as genai
from app.config import get_settings

settings = get_settings()

class AIProviderService:
    def __init__(self):
        self.openai = AsyncOpenAI(api_key=settings.openai_api_key)
        self.anthropic = AsyncAnthropic(api_key=settings.anthropic_api_key) if settings.anthropic_api_key else None
        # Google AI setup
        if settings.google_ai_api_key:
            genai.configure(api_key=settings.google_ai_api_key)

    async def chat_with_agent(
        self,
        stage_number: int,
        user_message: str,
        context: dict,
        model: str = "openai-gpt4o"
    ) -> dict:
        """Chat with an AI agent"""

        # Build messages
        messages = self._build_messages(stage_number, user_message, context)

        # Get tools for this agent
        tools = self._get_tools_for_agent(stage_number)

        # Call appropriate AI provider
        if model.startswith("openai"):
            return await self._chat_openai(messages, tools)
        elif model.startswith("anthropic"):
            return await self._chat_anthropic(messages, tools)
        elif model.startswith("google"):
            return await self._chat_google(messages, tools)
        else:
            raise ValueError(f"Unknown model: {model}")

    async def _chat_openai(self, messages: list, tools: list | None = None) -> dict:
        """Chat with OpenAI"""
        params = {
            "model": "gpt-4o",
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": 0.7
        }

        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"

        response = await self.openai.chat.completions.create(**params)

        # Handle tool calls if present
        if response.choices[0].message.tool_calls:
            # Execute tools and continue conversation
            pass

        return {
            "content": response.choices[0].message.content,
            "model": "openai-gpt4o",
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
```

### services/perplexity_search.py

```python
import httpx
from app.config import get_settings

settings = get_settings()

class PerplexitySearchService:
    def __init__(self):
        self.api_key = settings.perplexity_api_key
        self.base_url = "https://api.perplexity.ai"

    async def search(
        self,
        query: str,
        search_depth: str = "basic"
    ) -> dict:
        """
        Search using Perplexity AI

        Args:
            query: Search query in natural language
            search_depth: "basic" (sonar) or "advanced" (sonar-pro)

        Returns:
            {
                "answer": "Processed answer",
                "citations": ["url1", "url2"]
            }
        """
        model = "sonar-pro" if search_depth == "advanced" else "sonar"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that provides accurate and up-to-date information."
                        },
                        {
                            "role": "user",
                            "content": query
                        }
                    ],
                    "temperature": 0.2,
                    "max_tokens": 1000
                },
                timeout=30.0
            )

            data = response.json()

            return {
                "answer": data["choices"][0]["message"]["content"],
                "citations": data.get("citations", [])
            }
```

## Dependencies (dependencies.py)

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from app.database import get_db
from app.models.user import User
from app.config import get_settings

settings = get_settings()
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
```

## Dependencies (pyproject.toml con Poetry)

```toml
[tool.poetry]
name = "booms-backend"
version = "1.0.0"
description = "BOOMS Platform Backend API"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.109.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
sqlalchemy = {extras = ["asyncio"], version = "^2.0.25"}
alembic = "^1.13.1"
asyncpg = "^0.29.0"
pydantic = {extras = ["email"], version = "^2.5.0"}
pydantic-settings = "^2.1.0"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
httpx = "^0.26.0"
python-multipart = "^0.0.6"

# AI SDKs
openai = "^1.10.0"
anthropic = "^0.18.0"
google-generativeai = "^0.3.0"

# RAG & Embeddings
langchain = "^0.1.0"
sentence-transformers = "^2.3.0"
pypdf = "^3.17.0"

# PDF Generation
reportlab = "^4.0.0"
weasyprint = "^60.0"

# Excel Generation
openpyxl = "^3.1.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.4"
pytest-asyncio = "^0.23.0"
httpx = "^0.26.0"
black = "^24.0.0"
ruff = "^0.1.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

## Ejecutar Aplicación

```bash
# Instalar dependencias
poetry install

# Activar entorno virtual
poetry shell

# Ejecutar migraciones
alembic upgrade head

# Ejecutar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Ventajas vs Node.js

| Aspecto | Node.js + Express | FastAPI |
|---------|------------------|---------|
| **Async** | Callbacks/Promises | async/await nativo |
| **Type Safety** | TypeScript (opcional) | Python type hints |
| **Validación** | Manual o librerías | Pydantic (automático) |
| **AI SDKs** | Wrappers | Nativos |
| **RAG/Embeddings** | Limitado | Ecosistema completo |
| **ORM** | TypeORM, Prisma | SQLAlchemy (maduro) |
| **Docs API** | Manual | Automático (Swagger) |
| **Testing** | Jest | pytest (más poderoso) |

## Conclusión

FastAPI es la elección correcta para BOOMS porque:
- ✅ Python es el lenguaje de IA
- ✅ Async nativo para APIs de IA
- ✅ Ecosistema completo de ML/AI
- ✅ Mejor para RAG y embeddings
- ✅ Auto-documentación
- ✅ Type safety con Pydantic
