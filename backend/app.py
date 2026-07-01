import os
import sys
from pathlib import Path

from flask import Flask

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from backend.config import Config
    from backend.extensions import db, init_extensions
    from backend.routes import register_blueprints
else:
    from .config import Config
    from .extensions import db, init_extensions
    from .routes import register_blueprints


def create_app(config_class=None):
    if config_class is None:
        config_class = Config

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)
    app.config.setdefault("INSTANCE_FOLDER_PATH", app.instance_path)

    if app.config.get("SQLALCHEMY_DATABASE_URI", "").startswith("sqlite"):
        database_path = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "", 1)
        database_dir = os.path.dirname(database_path)
        if database_dir:
            os.makedirs(database_dir, exist_ok=True)

    init_extensions(app)
    register_blueprints(app)

    with app.app_context():
        if __package__ in (None, ""):
            import backend.models as models  # Import all models so SQLAlchemy registers them
        else:
            from . import models  # Import all models so SQLAlchemy registers them

        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
