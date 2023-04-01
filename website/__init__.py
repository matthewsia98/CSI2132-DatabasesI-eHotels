import os

import psycopg2
from flask import Flask

# from flask_sqlalchemy import SQLAlchemy

# DB_URL = os.environ.get("EHOTELS_DATABASE_URL")
# db = SQLAlchemy()

EHOTELS_DB_HOST = os.environ.get("EHOTELS_DB_HOST")
EHOTELS_DB_USER = os.environ.get("EHOTELS_DB_USER")
EHOTELS_DB_PASSWORD = os.environ.get("EHOTELS_DB_PASSWORD")
db = psycopg2.connect(
    host=EHOTELS_DB_HOST,
    port=5432,
    dbname="ehotels",
    user=EHOTELS_DB_USER,
    password=EHOTELS_DB_PASSWORD,
)


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret"

    # app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
    # db.init_app(app)

    from .auth import auth
    from .views import views

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    return app
