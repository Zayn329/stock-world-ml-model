from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
import os
from functools import lru_cache


class Settings(BaseSettings):
    # Project Information
    PROJECT_NAME: str = "Financial Insights Platform"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # Database Configuration
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/financial_insights"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # API Keys
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    FINANCIAL_MODELING_PREP_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    TWITTER_BEARER_TOKEN: Optional[str] = None

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_SENTIMENT: str = "sentiment_data"
    KAFKA_TOPIC_MARKET: str = "market_data"
    KAFKA_TOPIC_NEWS: str = "news_data"

    # ML Model Configuration
    MODEL_PATH: str = "./models"
    SENTIMENT_MODEL_NAME: str = "ProsusAI/finbert"
    HUGGINGFACE_CACHE_DIR: str = "./cache"
    BATCH_SIZE: int = 32

    # Real-time Configuration
    WEBSOCKET_ENABLED: bool = True
    MAX_CONNECTIONS: int = 1000

    # Monitoring and Logging
    PROMETHEUS_ENABLED: bool = True
    LOG_LEVEL: str = "INFO"

    # Data Sources
    YAHOO_FINANCE_ENABLED: bool = True
    REDDIT_ENABLED: bool = False
    TWITTER_ENABLED: bool = False

    # Feature Engineering
    GENETIC_ALGORITHM_POPULATION: int = 50
    GENETIC_ALGORITHM_GENERATIONS: int = 20

    # Model Training
    RETRAIN_INTERVAL_HOURS: int = 24
    MODEL_DRIFT_THRESHOLD: float = 0.1

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Global settings instance
settings = get_settings()