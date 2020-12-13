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


class TestAggregateByMonthAndStateAndAdd:

    imports_path = 'dashboard/tests/IMP_2019-sample.csv'
    products_path = 'dashboard/tests/NCM-sample-iso-8859-1.csv'
    states_path = 'dashboard/tests/UF-sample-iso-8859-1.csv'

    def test_top_product_by_month_and_state(self, db, runner):
        result = runner.invoke(args=[
            'data',
            'aggregate-by-month-and-state-and-add',
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
        expected = ('Finished ranking of products imported in 2019 by month '
                    'and state.')
        assert expected in result.output

        query = 'SELECT * FROM top_by_state_and_month'
        expected = [
            ('GO', 'Goiás', 2019, 1, 'import', 29393010, 'Cafeína', 237),
            ('GO', 'Goiás', 2019, 4, 'import', 29393010, 'Cafeína', 882),
            ('GO', 'Goiás', 2019, 6, 'import', 29393010, 'Cafeína', 2964),
            ('GO', 'Goiás', 2019, 11, 'import', 29393010, 'Cafeína', 252),
            ('GO', 'Goiás', 2019, 2, 'import', 29061100, 'Mentol', 2028),
            ('GO', 'Goiás', 2019, 5, 'import', 29061100, 'Mentol', 1292),
            ('GO', 'Goiás', 2019, 7, 'import', 29061100, 'Mentol', 466),
            ('GO', 'Goiás', 2019, 8, 'import', 29061100, 'Mentol', 2340),
            ('RJ', 'Rio de Janeiro', 2019, 1, 'import', 90153000, 'Níveis',
             72),
            ('RJ', 'Rio de Janeiro', 2019, 2, 'import', 90153000, 'Níveis',
             2111),
            ('RJ', 'Rio de Janeiro', 2019, 7, 'import', 90153000, 'Níveis',
             664),
            ('RJ', 'Rio de Janeiro', 2019, 10, 'import', 90153000, 'Níveis',
             2188),
            ('RJ', 'Rio de Janeiro', 2019, 4, 'import', 19059020, 'Bolachas',
             942),
            ('RJ', 'Rio de Janeiro', 2019, 9, 'import', 19059020, 'Bolachas',
             2239),
            ('RJ', 'Rio de Janeiro', 2019, 5, 'import', 48202000, 'Cadernos',
             42),
            ('RJ', 'Rio de Janeiro', 2019, 6, 'import', 48202000, 'Cadernos',
             1202),
            ('SC', 'Santa Catarina', 2019, 1, 'import', 48202000, 'Cadernos',
             1872),
            ('SC', 'Santa Catarina', 2019, 7, 'import', 48202000, 'Cadernos',
             84),
            ('SC', 'Santa Catarina', 2019, 8, 'import', 48202000, 'Cadernos',
             8974),
            ('SC', 'Santa Catarina', 2019, 10, 'import', 48202000, 'Cadernos',
             4855),
            ('RJ', 'Rio de Janeiro', 2019, 11, 'import', 22086000, 'Vodca',
             6458),
            ('RJ', 'Rio de Janeiro', 2019, 12, 'import', 22086000, 'Vodca',
             25024),
            ('SC', 'Santa Catarina', 2019, 2, 'import', 96091000, 'Lápis',
             274563),
            ('SC', 'Santa Catarina', 2019, 4, 'import', 96091000, 'Lápis',
             828),
            ('SC', 'Santa Catarina', 2019, 5, 'import', 96091000, 'Lápis',
             623828),
            ('SC', 'Santa Catarina', 2019, 9, 'import', 96091000, 'Lápis',
             36593),
            ('SC', 'Santa Catarina', 2019, 11, 'import', 96091000, 'Lápis',
             371146),
            ('SC', 'Santa Catarina', 2019, 3, 'import', 84831040, 'Manivelas',
             1054),
            ('SC', 'Santa Catarina', 2019, 6, 'import', 84831040, 'Manivelas',
             1715),
            ('TO', 'Tocantins', 2019, 1, 'import', 90051000, 'Binóculos', 530),
            ('TO', 'Tocantins', 2019, 3, 'import', 90051000, 'Binóculos', 460),
            ('TO', 'Tocantins', 2019, 5, 'import', 90051000, 'Binóculos', 757),
            ('TO', 'Tocantins', 2019, 6, 'import', 90051000, 'Binóculos', 714),
            ('TO', 'Tocantins', 2019, 8, 'import', 90051000, 'Binóculos', 5638)
        ]
        actual = db.engine.execute(query).fetchall()
        assert actual == expected


class TestAggregateStateContributionsAndAdd:

    imports_path = 'dashboard/tests/IMP_2019-sample.csv'
    products_path = 'dashboard/tests/NCM-sample-iso-8859-1.csv'
    states_path = 'dashboard/tests/UF-sample-iso-8859-1.csv'

    def test_top_product_by_month_and_state(self, db, runner):
        result = runner.invoke(args=[
            'data',
            'aggregate-state-contributions-and-add',
            self.imports_path,
            self.states_path,
            '--kind',
            'import',
            '--year',
            2019
        ])
        expected = ('Finished aggregation of states contributions to the '
                    'imports in 2019')
        assert expected in result.output

        query = 'SELECT * FROM state_contributions'
        expected = [
            ('import', 2019, 'GO', 'Goiás', 11624, 0.7988377542927908),
            ('import', 2019, 'RJ', 'Rio de Janeiro', 43145, 2.96505978225761),
            ('import', 2019, 'SC', 'Santa Catarina', 1392246,
             95.67951377005512),
            ('import', 2019, 'TO', 'Tocantins', 8099, 0.5565886933944695),
        ]
        actual = db.engine.execute(query).fetchall()
        assert actual == expected
