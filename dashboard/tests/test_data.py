import pytest
from src.commands.data import get_products, get_states


class TestGetProducts:

    csv_path = 'dashboard/tests/NCM-sample-iso-8859-1.csv'

    def test_for_product_columns(self):
        products = get_products(self.csv_path)
        assert set(products.columns) == {'product_code', 'product'}

    def test_for_number_of_products(self):
        products = get_products(self.csv_path)
        assert len(products) == 10

    def test_for_specific_product(self):
        products = get_products(self.csv_path)
        assert 27111100 in products['product_code'].values
        assert 'Gás natural liquefeito' in products['product'].values


class TestGetStates:

    csv_path = 'dashboard/tests/UF-sample-iso-8859-1.csv'

    def test_for_state_columns(self):
        states = get_states(self.csv_path)
        assert set(states.columns) == {'state', 'state_code'}

    def test_for_number_of_states(self):
        states = get_states(self.csv_path)
        assert len(states) == 6

    def test_for_specific_state(self):
        states = get_states(self.csv_path)
        assert 'SP' in states['state_code'].values
        assert 'São Paulo' in states['state'].values
