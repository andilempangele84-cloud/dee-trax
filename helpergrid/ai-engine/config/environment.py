#!/usr/bin/env python3
"""
Environment Configuration Management

Handles all environment variables and configuration settings
for the AI Engine application.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """
    Application Settings - Loaded from environment variables
    """
    
    # Application
    APP_NAME: str = "HelperGrid AI Engine"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", description="dev, staging, production")
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:3001",
    ]
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/helpergrid_ai"
    MONGODB_URL: str = "mongodb://localhost:27017/helpergrid_ai"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # LLM Providers
    OPENAI_API_KEY: str = ""
    OPENAI_ORG_ID: Optional[str] = None
    ANTHROPIC_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    REPLICATE_API_TOKEN: str = ""
    
    # Vector Database
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "gcp-starter"
    PINECONE_INDEX_NAME: str = "helpergrid-embeddings"
    
    WEAVIATE_URL: str = "http://localhost:8080"
    
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    
    # Vector Store
    VECTOR_DB_TYPE: str = Field(default="pinecone", description="pinecone, weaviate, milvus, faiss")
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # Authentication
    JWT_SECRET_KEY: str = "your_jwt_secret_key_change_this_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # LLM Configuration
    DEFAULT_LLM_PROVIDER: str = "openai"
    DEFAULT_MODEL: str = "gpt-4"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2000
    TOP_P: float = 0.9
    
    # Cache
    REDIS_TTL_SECONDS: int = 3600
    CACHE_ENABLED: bool = True
    
    # Feature Flags
    EXPERIMENTAL_FEATURES: bool = False
    RAG_ENABLED: bool = True
    FINE_TUNING_ENABLED: bool = True
    CUSTOM_MODELS_ENABLED: bool = True
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    WANDB_API_KEY: Optional[str] = None
    WANDB_PROJECT: str = "helpergrid-ai"
    
    # API Keys
    STRIPE_API_KEY: str = ""
    MAILGUN_API_KEY: str = ""
    TWILIO_API_KEY: str = ""
    SLACK_BOT_TOKEN: str = ""
    GOOGLE_CALENDAR_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        if v not in ["development", "staging", "production"]:
            raise ValueError("ENVIRONMENT must be development, staging, or production")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()


# Global settings instance
settings = Settings()
