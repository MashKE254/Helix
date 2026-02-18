"""
Application configuration
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Helix"
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Database
    DATABASE_URL: str = "postgresql://helix:helix@localhost:5432/helix"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Anthropic API
    ANTHROPIC_API_KEY: str = ""
    
    # OpenAI API (for embeddings)
    OPENAI_API_KEY: str = ""
    
    # Model routing thresholds
    HAIKU_THRESHOLD: float = 0.3  # Simple queries
    SONNET_THRESHOLD: float = 0.7  # Standard queries
    OPUS_THRESHOLD: float = 1.0    # Complex queries
    
    # Vector DB
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Verification services
    WOLFRAM_APP_ID: str = ""
    JUDGE0_API_URL: str = "https://judge0-ce.p.rapidapi.com"
    JUDGE0_API_KEY: str = ""
    
    # Curriculum sources
    CURRICULUM_DATA_DIR: str = "./data/curriculum"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
