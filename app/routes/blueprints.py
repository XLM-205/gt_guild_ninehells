from flask import Flask
from routes.auth import auth
from routes.main import main
from routes.raid import raid

def init_blueprints(flask_app: Flask) -> None:
    flask_app.register_blueprint(auth)
    flask_app.register_blueprint(raid)
    flask_app.register_blueprint(main)
    