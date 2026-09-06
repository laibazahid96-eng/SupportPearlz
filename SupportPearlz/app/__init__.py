import logging
import os
from pathlib import Path

from flask import Flask

from app.config import CONFIG_BY_NAME
from app.extensions import csrf, limiter, sess
from app.services.knowledge import KnowledgeBase


def create_app(config_name: str | None = None) -> Flask:
    config_name = config_name or os.environ.get("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(CONFIG_BY_NAME[config_name])

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    Path(app.config["SESSION_FILE_DIR"]).mkdir(parents=True, exist_ok=True)

    sess.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    app.extensions["knowledge_base"] = KnowledgeBase(app.config["KNOWLEDGE_BASE_PATH"])

    from app.routes import bp as main_bp

    app.register_blueprint(main_bp)

    return app
