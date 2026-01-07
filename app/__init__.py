from flask import Flask
from app.config import Config
from app.models import db
from app.routes import api
from flasgger import Swagger
import logging

logging.basicConfig(level=logging.INFO)


def create_app():
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

    Swagger(app, config=swagger_config, template=swagger_template)

    db.init_app(app)

    with app.app_context():
        db.create_all()  # creates tables if not exist

    app.register_blueprint(api)
    return app
