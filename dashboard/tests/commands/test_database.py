from src.database import db


class TestCreate:

    def test_tables_created(self, runner):
        expected = []
        assert expected == db.engine.table_names()

        result = runner.invoke(args=['database', 'create'])

        expected = [
            'state_contributions',
            'top_by_state_and_month',
            'top_by_state_and_year'
        ]
        assert expected == db.engine.table_names()
        assert 'All tables were created' in result.output


class TestDrop:

    def test_confirm(self, db, runner):
        expected = [
            'state_contributions',
            'top_by_state_and_month',
            'top_by_state_and_year'
        ]
        assert expected == db.engine.table_names()

        result = runner.invoke(args=['database', 'drop'], input='y')

        expected = []
        assert expected == db.engine.table_names()
        assert 'All tables were dropped' in result.output

    def test_abort(self, db, runner):

        expected = [
            'state_contributions',
            'top_by_state_and_month',
            'top_by_state_and_year'
        ]
        assert expected == db.engine.table_names()
        result = runner.invoke(args=['database', 'drop'], input='N')
        assert 'Aborted!' in result.output
        assert expected == db.engine.table_names()
