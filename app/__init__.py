from flask import Flask
from app.config import Config
from app.models import db
from app.routes import api
from flasgger import Swagger
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Swagger configuration
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/swagger/",
    }

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Async Summarizer API",
            "description": "API for asynchronous content summarization",
            "version": "1.0.0",
        },
        "basePath": "/",
        "schemes": ["http", "https"],
    }

    # Initialize Swagger
    Swagger(app, config=swagger_config, template=swagger_template)

    # Initialize database
    db.init_app(app)

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    # Register API routes
    app.register_blueprint(api)

    return app
