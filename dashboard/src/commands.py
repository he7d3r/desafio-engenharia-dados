import click
from src.database import db


def create_db():
    """Create a database with the appropriate tables"""
    db.create_all()


def drop_db():
    """Drop all tables from database"""
    db.drop_all()


def init_app(app):
    # add multiple commands in a bulk
    for command in [create_db, drop_db]:
        app.cli.add_command(app.cli.command()(command))
