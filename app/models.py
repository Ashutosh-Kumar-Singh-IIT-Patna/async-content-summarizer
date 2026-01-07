from flask_sqlalchemy import SQLAlchemy
import uuid
from enum import Enum
from datetime import datetime

db = SQLAlchemy()


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ContentType(str, Enum):
    TEXT = "text"
    URL = "url"


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(
        db.String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    content_hash = db.Column(db.String, index=True, nullable=True)
    content_type = db.Column(db.Enum(ContentType), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum(JobStatus), nullable=False)
    cached = db.Column(db.Boolean, default=False, nullable=False)
    processing_time_ms = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
