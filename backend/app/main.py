# /backend/app/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.database import get_db

settings = get_settings()

app = FastAPI(
    title="BOOMS Platform API",
    description="AI-powered marketing onboarding platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
    try:
        from sqlalchemy import text
        from app.models.user import User
        # Check basic connection
        await db.execute(text("SELECT 1"))
        # Check if table exists
        await db.execute(select(User).limit(1))
        db_status = "connected_and_migrated"
    except Exception as e:
        db_status = f"error: {str(e)}"
        
    return {
        "status": "healthy",
        "database": db_status,
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
