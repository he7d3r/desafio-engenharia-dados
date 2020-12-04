import os

from flask import Flask

from src import commands, database, routes
from src.config import config


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV') or 'production'
    print(f'app.create_app({config_name})')
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    from src import model
    database.init_app(app)
    commands.init_app(app)
    routes.init_app(app)

    return app
