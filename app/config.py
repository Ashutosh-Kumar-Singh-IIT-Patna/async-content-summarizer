import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration from environment variables"""

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    # Redis configuration
    REDIS_URL = os.getenv("REDIS_URL")

    # Celery configuration
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

    # LLM configuration
    LLM_TOKEN = os.getenv("LLM_TOKEN")
    LLM_ENDPOINT = os.getenv("LLM_ENDPOINT")
    LLM_MODEL = os.getenv("LLM_MODEL")
