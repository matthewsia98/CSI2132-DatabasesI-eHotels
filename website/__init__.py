import psycopg2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

DB_URL = f"postgresql+psycopg2://msia:m477h3w5@localhost:5432/ehotels"
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL

    db.init_app(app)

    from .auth import auth
    from .views import views

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    return app


def get_db_connection():
    conn = psycopg2.connect(
        # host="ehotelsdb.cjlormfzlvp4.ca-central-1.rds.amazonaws.com",
        host="localhost",
        database="ehotels",
        # user="postgres",
        # password="ehotelsdbpassword",
        user="msia",
        password="m477h3w5",
        port="5432",
    )
    return conn
