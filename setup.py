from setuptools import setup
from website.web_config import defaults

setup(
    name="guild_docker",
    version=defaults["INTERNAL"]["VERSION"],
    author="Ramon Darwich de Menezes",
    description="Manages the Guild Database under a website",
    license="GNU",
    install_requires=["flask", "flask-sqlalchemy", "flask-login", "requests",
                      "werkzeug", "sqlalchemy", "flask-sslify", "gunicorn"],
    entry_points={
        "console_scripts": [
            # <Nome do Comando>=<Modulo (Arquivo)>:<Funcao>
            "run_webpage=startup:main"
        ]
    }
)
