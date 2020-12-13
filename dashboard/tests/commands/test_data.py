from src.commands.data import get_products, get_states


class TestGetProducts:

    csv_path = 'dashboard/tests/NCM-sample-iso-8859-1.csv'

    def test_for_product_columns(self):
        products = get_products(self.csv_path)
        actual = set(products.columns)
        expected = {'product_code', 'product'}
        assert actual == expected

    def test_for_product_codes(self):
        products = get_products(self.csv_path)
        actual = list(products['product_code'].values)
        expected = [22086000, 19059020, 29393010, 29061100, 48202000,
                    84831040, 96091000, 90153000, 90051000]
        assert actual == expected

    def test_for_product_names(self):
        products = get_products(self.csv_path)
        actual = list(products['product'].values)
        expected = ['Vodca', 'Bolachas', 'Cafeína', 'Mentol', 'Cadernos',
                    'Manivelas', 'Lápis', 'Níveis', 'Binóculos']
        assert actual == expected


class TestGetStates:

    csv_path = 'dashboard/tests/UF-sample-iso-8859-1.csv'

    def test_for_state_columns(self):
        states = get_states(self.csv_path)
        actual = set(states.columns)
        expected = {'state', 'state_code'}
        assert actual == expected

    def test_for_state_codes(self):
        states = get_states(self.csv_path)
        actual = list(states['state_code'].values)
        expected = ['TO', 'RJ', 'SC', 'GO', 'ZN']
        assert actual == expected

    def test_for_state_names(self):
        states = get_states(self.csv_path)
        actual = list(states['state'].values)
        expected = ['Tocantins', 'Rio de Janeiro', 'Santa Catarina', 'Goiás',
                    'Zona Não Declarada']
        assert actual == expected


class TestAggregateByStateAndAdd:

    imports_path = 'dashboard/tests/IMP_2019-sample.csv'
    products_path = 'dashboard/tests/NCM-sample-iso-8859-1.csv'
    states_path = 'dashboard/tests/UF-sample-iso-8859-1.csv'

    def test_top_product_by_state(self, db, runner):
        result = runner.invoke(args=[
            'data',
            'aggregate-by-state-and-add',
            self.imports_path,
            self.states_path,
            self.products_path,
            '--kind',
            'import',
            '--year',
            2019,
            '--n',
            1
        ])
        expected = 'Finished ranking of products imported in 2019 by state.'
        assert expected in result.output

        query = 'SELECT * FROM top_by_state_and_year'
        expected = [
            ('GO', 'Goiás', 2019, 'import', 29061100, 'Mentol', 6126),
            ('RJ', 'Rio de Janeiro', 2019, 'import', 22086000, 'Vodca', 32096),
            ('SC', 'Santa Catarina', 2019, 'import', 96091000, 'Lápis',
             1306958),
            ('TO', 'Tocantins', 2019, 'import', 90051000, 'Binóculos', 8099)]
        actual = db.engine.execute(query).fetchall()
        assert actual == expected
