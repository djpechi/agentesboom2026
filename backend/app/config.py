# /backend/app/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_days: int = 7

    # AI
    openai_api_key: str
    google_ai_api_key: str | None = None
    perplexity_api_key: str | None = None

    # CORS
    cors_origins: str = '["http://localhost:5173"]'

    # Debug
    debug_mode: bool = False

    class Config:
        env_file = ".env"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from string to list"""
        import json
        return json.loads(self.cors_origins)


@lru_cache()
def get_settings():
    return Settings()
