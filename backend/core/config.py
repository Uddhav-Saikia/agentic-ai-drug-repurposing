"""
Configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Agentic AI Drug Repurposing"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    
    # Server
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "drug_repurposing"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres123"
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres123@localhost:5432/drug_repurposing"
    )
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # External APIs
    CLINICAL_TRIALS_API_KEY: Optional[str] = None
    USPTO_API_KEY: Optional[str] = None
    PUBMED_API_KEY: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-min-32-characters-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Agent Configuration
    MAX_CONCURRENT_AGENTS: int = 4
    AGENT_TIMEOUT_SECONDS: int = 300
    ENABLE_AGENT_MEMORY: bool = True
    
    # Vector Database
    VECTOR_DB_TYPE: str = "pgvector"
    VECTOR_DIMENSION: int = 1536
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
