import os
from flask import Flask
from app.routes import main
from app.db import init_db


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config["DATABASE"] = os.path.join(app.instance_path, "trainingslog.db")
    app.register_blueprint(main)
    init_db(app.config["DATABASE"])
    return app
