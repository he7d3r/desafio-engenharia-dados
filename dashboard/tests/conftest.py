import pytest
from src import create_app
from src.database import db as _db
from src.model import StateContributions, TopByStateAndYear


@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        yield app


@pytest.fixture(scope='session')
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def db(app):
    _db.create_all()
    yield _db
    _db.drop_all()


@pytest.fixture(scope='function')
def client(app, db):
    add_sample_data(db)
    yield app.test_client()


def add_sample_data(db):
    state_contributions = [
        StateContributions(
            kind='import',
            year=2019,
            state_code='SP',
            state='São Paulo',
            total=123456789,
            percentage=4.2
        ),
        StateContributions(
            kind='export',
            year=2019,
            state_code='SP',
            state='São Paulo',
            total=111222333,
            percentage=4.44
        )
    ]
    top_products = [
        TopByStateAndYear(
            state_code='SP',
            state='São Paulo',
            year=2019,
            kind='import',
            product_code='01064100',
            product='Abelhas',
            total=100200300
        ),
        TopByStateAndYear(
            state_code='SP',
            state='São Paulo',
            year=2019,
            kind='export',
            product_code='01064100',
            product='Abelhas',
            total=300200100
        ),
        TopByStateAndYear(
            state_code='SP',
            state='São Paulo',
            year=2018,
            kind='import',
            product_code='01064100',
            product='Abelhas',
            total=100200300
        ),
        TopByStateAndYear(
            state_code='SP',
            state='São Paulo',
            year=2018,
            kind='export',
            product_code='01064100',
            product='Abelhas',
            total=300200100
        )
    ]
    db.session.add_all(state_contributions)
    db.session.add_all(top_products)
    db.session.commit()
