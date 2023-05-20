import os
from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from app.services.log import log_critical


db = SQLAlchemy()

def init_db(flask_app: Flask) -> None:
    """Initializes the Database"""
    
    # db_uri = os.environ.get("LOCAL_DATABASE_URL", "")
    db_uri = os.environ.get("DATABASE_URL", "")
    
    if db_uri is not None and db_uri != "":
        flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
        flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db.init_app(flask_app)

    else:   # No database! Aborting...
        log_critical(comment="No database detected, aborting startup...")
        os.abort()