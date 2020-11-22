from src.commands import database, data


def init_app(app):
    database.init_app(app)
    data.init_app(app)
