import click
from flask.cli import AppGroup
from src.database import db


def init_app(app):
    database_cli = AppGroup('database',
                            short_help='Commands to manage the database')

    @database_cli.command()
    def create():
        """Create a database with the appropriate tables"""
        db.create_all()
        click.echo('All tables were created.')

    @database_cli.command()
    @click.confirmation_option(
        prompt='Do you really want to drop all tables?'
    )
    def drop():
        """Drop all database tables"""
        db.drop_all()
        click.echo('All tables were dropped.')
    app.cli.add_command(database_cli)
