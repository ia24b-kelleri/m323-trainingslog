"""Flask-App-Factory für das Trainingslog."""
import os

from flask import Flask

from app.db import init_db


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev-m323-trainingslog",
        DATABASE=os.path.join(app.instance_path, "trainingslog.db"),
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,  # max. 2 MB für CSV-Upload
    )
    if test_config:
        app.config.update(test_config)

    init_db(app.config["DATABASE"])

    from app.routes import bp
    app.register_blueprint(bp)
    return app
