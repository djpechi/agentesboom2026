# /backend/app/routers/__init__.py

from app.routers.auth import router as auth_router
from app.routers.accounts import router as accounts_router
from app.routers.stages import router as stages_router
from app.routers.agents import router as agents_router
from app.routers.exports import router as exports_router
from app.routers.demo import router as demo_router

__all__ = ["auth_router", "accounts_router", "stages_router", "agents_router", "exports_router", "demo_router"]
