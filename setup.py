from setuptools import setup
from config.app_defaults import app_defaults

setup(
    name="guild_docker",
    version=app_defaults["INTERNAL"]["VERSION"],
    author="Ramon Darwich de Menezes",
    description="Manages the Guild Database under a app",
    license="GNU",
    install_requires=["flask",    "flask-sqlalchemy", "flask-login", "flask-sslify",
                      "requests", "werkzeug",         "sqlalchemy",  "gunicorn",
                      "psycopg2-binary"],
    entry_points={
        "console_scripts": [
            "run_webpage=app:main"
        ]
    }
)
