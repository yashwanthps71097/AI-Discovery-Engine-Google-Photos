import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Path to the project root .env
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

class Settings(BaseSettings):
    # Application Configuration
    APP_NAME: str = "AI-Powered Discovery Engine for Google Photos Retrieval"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "discovery_engine_secret_dev_key")

    # Groq API Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL_EXTRACTION: str = os.getenv("GROQ_MODEL_EXTRACTION", "openai/gpt-oss-120b")
    GROQ_MODEL_FAST_FILTER: str = os.getenv("GROQ_MODEL_FAST_FILTER", "openai/gpt-oss-20b")
    GROQ_MODEL_SYNTHESIS: str = os.getenv("GROQ_MODEL_SYNTHESIS", "openai/gpt-oss-120b")

    # Database Configuration (Defaults to SQLite for local development without Docker)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{PROJECT_ROOT / 'discovery_engine.db'}"
    )

    # Cache & Vector Store
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    VECTOR_DB_URL: str = os.getenv("VECTOR_DB_URL", "http://localhost:6333")

    # Scraping & Ingestion Limits
    MAX_REQUESTS_PER_MINUTE_REDDIT: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE_REDDIT", "30"))
    MAX_REQUESTS_PER_MINUTE_PLAYSTORE: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE_PLAYSTORE", "60"))
    INGESTION_BATCH_SIZE: int = int(os.getenv("INGESTION_BATCH_SIZE", "100"))

    # Epistemic Confidence Thresholds
    MIN_RELEVANCE_SCORE: float = 0.70

    class Config:
        case_sensitive = True

settings = Settings()
