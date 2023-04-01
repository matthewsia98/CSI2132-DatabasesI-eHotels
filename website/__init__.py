import os

import psycopg2
from flask import Flask

EHOTELS_DB_HOST = os.environ.get("EHOTELS_DB_HOST")
EHOTELS_DB_USER = os.environ.get("EHOTELS_DB_USER")
EHOTELS_DB_PASSWORD = os.environ.get("EHOTELS_DB_PASSWORD")
db = None


def create_app(remote=False):
    global db, EHOTELS_DB_HOST

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret"

    if not remote:
        EHOTELS_DB_HOST = "localhost"

    db = psycopg2.connect(
        host=EHOTELS_DB_HOST,
        port=5432,
        dbname="ehotels",
        user=EHOTELS_DB_USER,
        password=EHOTELS_DB_PASSWORD,
    )

    from .auth import auth
    from .views import views

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    return app
