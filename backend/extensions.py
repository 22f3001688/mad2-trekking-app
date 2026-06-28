from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()


def init_extensions(app):
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
