from setuptools import setup

setup(
    name="guild_docker",
    version="0.1.0",
    author="Ramon Darwich de Menezes",
    description="Manages the Guild Database",
    license="GNU",
    install_requires=["flask", "flask-sqlalchemy", "flask-login", "requests",
                      "werkzeug", "sqlalchemy", "flask-sslify"],
    entry_points={
        "console_scripts": [
            # <Nome do Comando>=<Modulo (Arquivo)>:<Funcao>
            "run_webpage=server_boot:create_app"
        ]
    }
)