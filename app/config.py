import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    REDIS_URL = os.getenv("REDIS_URL")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

    LLM_TOKEN = os.getenv("LLM_TOKEN")
    LLM_ENDPOINT = os.getenv("LLM_ENDPOINT")
    LLM_MODEL = os.getenv("LLM_MODEL")
