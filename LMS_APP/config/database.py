from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

db = SQLAlchemy()

def init_db(app):
    password = quote_plus(os.getenv("DB_PASSWORD"))
    database_name = os.getenv("DB_NAME")

    if app.config.get("TESTING") or os.getenv("TESTING") == "1":
        database_name = os.getenv("TEST_DB_NAME")

    app.config["SQLALCHEMY_DATABASE_URI"] = ("mysql+mysqlconnector://"+ os.getenv("DB_USER")+ ":"+ password+ "@"+ os.getenv("DB_HOST")+ "/"+ database_name)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)