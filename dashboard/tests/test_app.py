from datetime import datetime

import pytest
from src import create_app
from src.database import db
from src.model import StateContributions, TopByStateAndYear
from src.routes import get_month_name, large_num_formatter


class TestGetMonthName:

    def test_for_valid_month_values(self):
        assert get_month_name(1) == 'janeiro'
        assert get_month_name(12) == 'dezembro'

    def test_for_invalid_month_values(self):
        for value in [0, 13, 'outro', '*']:
            assert get_month_name(value) == 'todos os meses'

    def test_for_return_type(self):
        for month in range(1, 13):
            assert isinstance(get_month_name(month), str)


class TestLargeNumFormatter:
    def test_for_formatting_of_number_under_a_thousand(self):
        # FIXME: Remove whitespaces
        assert large_num_formatter(1) == '1.0 '
        assert large_num_formatter(42) == '42.0 '
        assert large_num_formatter(999) == '999.0 '

    def test_for_formatting_of_number_under_a_million(self):
        assert large_num_formatter(1000) == '1.0 mil'
        assert large_num_formatter(42000) == '42.0 mil'
        assert large_num_formatter(999949) == '999.9 mil'
        # FIXME: Format '1000.0 mil' as '1.0 Mi.'
        assert large_num_formatter(999950) == '1000.0 mil'

    def test_for_formatting_of_number_under_a_billion(self):
        assert large_num_formatter(1000000) == '1.0 Mi.'
        assert large_num_formatter(4200420) == '4.2 Mi.'
        assert large_num_formatter(999949999) == '999.9 Mi.'
        # FIXME: Format '1000.0 Mi.' as '1.0 Bi.'
        assert large_num_formatter(999950000) == '1000.0 Mi.'

    def test_for_formatting_of_number_under_a_trillion(self):
        assert large_num_formatter(1000000000) == '1.0 Bi.'
        assert large_num_formatter(420420420420) == '420.4 Bi.'
        assert large_num_formatter(999949999999) == '999.9 Bi.'
        # FIXME: Format '1000.0 Bi.' as '1.0 Tri.'
        assert large_num_formatter(999950000000) == '1000.0 Bi.'

    def test_for_formatting_of_number_over_a_trillion(self):
        assert large_num_formatter(1000000000000) == '1.0 Tri.'
        assert large_num_formatter(420420420420000) == '420.4 Tri.'
        assert large_num_formatter(999949999999999) == '999.9 Tri.'
        assert large_num_formatter(999950000000000) == '1000.0 Tri.'


@pytest.fixture
def client():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        contrib1 = StateContributions(
            kind='import',
            year=2019,
            state_code='SP',
            state='São Paulo',
            total=123456789,
            percentage=4.2
        )
        contrib2 = StateContributions(
            kind='export',
            year=2019,
            state_code='SP',
            state='São Paulo',
            total=111222333,
            percentage=4.44
        )
        top1 = TopByStateAndYear(
            state_code='SP',
            state='São Paulo',
            year=2019,
            kind='import',
            product_code='01064100',
            product='Abelhas',
            total=100200300
        )
        top2 = TopByStateAndYear(
            state_code='SP',
            state='São Paulo',
            year=2019,
            kind='export',
            product_code='01064100',
            product='Abelhas',
            total=300200100
        )
        top3 = TopByStateAndYear(
            state_code='SP',
            state='São Paulo',
            year=2018,
            kind='import',
            product_code='01064100',
            product='Abelhas',
            total=100200300
        )
        top4 = TopByStateAndYear(
            state_code='SP',
            state='São Paulo',
            year=2018,
            kind='export',
            product_code='01064100',
            product='Abelhas',
            total=300200100
        )
        db.session.add(contrib1)
        db.session.add(contrib2)
        db.session.add(top1)
        db.session.add(top2)
        db.session.add(top3)
        db.session.add(top4)
        db.session.commit()

        yield app.test_client()
        db.drop_all()


class TestSomeRoutes:
    def test_missing_page(self, client):
        response = client.get('/random_missing_page')
        assert response.status_code == 404
        assert bytes('Página Não Encontrada', 'utf-8') in response.data

    def test_home_page_redirect(self, client):
        response = client.get('/')

        large_state_code = 'SP'
        previous_year = datetime.now().year - 1
        target_url = f'/dashboard/{large_state_code}/{previous_year}'

        assert response.status_code == 302
        assert response.location.endswith(target_url)

    def test_year_without_national_statistics(self, client):
        response = client.get('/dashboard/SP/2018')
        assert response.status_code == 200
        assert b'Dashboard' in response.data
        assert bytes('Estatísticas nacionais', 'utf-8') not in response.data
        assert bytes('Estatísticas estaduais', 'utf-8') in response.data
