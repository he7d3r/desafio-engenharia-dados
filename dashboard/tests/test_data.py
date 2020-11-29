import pytest
from src.commands.data import get_products, get_states


def test_for_product_columns():
    fake_csv = 'dashboard/tests/NCM-sample-iso-8859-1.csv'
    products = get_products(fake_csv)
    assert set(products.columns) == {'product_code', 'product'}


def test_for_number_of_products():
    fake_csv = 'dashboard/tests/NCM-sample-iso-8859-1.csv'
    products = get_products(fake_csv)
    assert len(products) == 10


def test_for_specific_product():
    fake_csv = 'dashboard/tests/NCM-sample-iso-8859-1.csv'
    products = get_products(fake_csv)
    assert 27111100 in products['product_code'].values
    assert 'Gás natural liquefeito' in products['product'].values


def test_for_state_columns():
    fake_csv = 'dashboard/tests/UF-sample-iso-8859-1.csv'
    states = get_states(fake_csv)
    assert set(states.columns) == {'state', 'state_code'}


def test_for_number_of_states():
    fake_csv = 'dashboard/tests/UF-sample-iso-8859-1.csv'
    states = get_states(fake_csv)
    assert len(states) == 6


def test_for_specific_state():
    fake_csv = 'dashboard/tests/UF-sample-iso-8859-1.csv'
    states = get_states(fake_csv)
    assert 'SP' in states['state_code'].values
    assert 'São Paulo' in states['state'].values
