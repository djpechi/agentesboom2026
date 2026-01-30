# /backend/app/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.database import get_db

settings = get_settings()

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    from app.database import engine, Base
    from app.models import user, account, stage
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="BOOMS Platform API",
    description="AI-powered marketing onboarding platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
# CORS middleware
origins = [
    "http://localhost:5173", 
    "http://127.0.0.1:5173", 
    "http://0.0.0.0:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

# Add origins from settings
try:
    origins.extend(settings.cors_origins_list)
except Exception:
    pass

# Deduplicate origins
origins = list(set(origins))

# If "*" is in origins, allow_credentials must be False
allow_all_origins = "*" in origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=not allow_all_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "BOOMS Platform API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    """Health check endpoint"""
    db_status = "unknown"
    tables = []
    try:
        from sqlalchemy import text
        # Check basic connection
        await db.execute(text("SELECT 1"))
        
        # List tables in public schema
        result = await db.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'"))
        tables = [row[0] for row in result]
        
        db_status = "connected"
        if "users" in tables:
            db_status = "connected_and_migrated"
    except Exception as e:
        db_status = f"error: {str(e)}"
        
    return {
        "status": "healthy",
        "database": db_status,
        "tables": tables,
        "openai": "configured" if settings.openai_api_key != "your-openai-api-key-here" else "not configured"
    }


# Include routers
from app.routers import auth_router, accounts_router, stages_router, agents_router, exports_router, demo_router

app.include_router(auth_router)
app.include_router(accounts_router)
app.include_router(stages_router)
app.include_router(agents_router)
app.include_router(exports_router)
app.include_router(demo_router)
