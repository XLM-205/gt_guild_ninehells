from flask import Flask
from app.routes.auth import auth
from app.routes.main import main
from app.routes.raid import raid

def init_blueprints(flask_app: Flask) -> None:
    flask_app.register_blueprint(auth)
    flask_app.register_blueprint(raid)
    flask_app.register_blueprint(main)
    