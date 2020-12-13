from src.database import db


class TestCreate:

    def test_tables_created(self, runner):
        # Before running the command
        actual = db.engine.table_names()
        expected = []
        assert actual == expected

        # After running the command
        result = runner.invoke(args=['database', 'create'])
        actual = db.engine.table_names()
        expected = [
            'state_contributions',
            'top_by_state_and_month',
            'top_by_state_and_year'
        ]
        assert actual == expected
        assert 'All tables were created' in result.output


class TestDrop:

    def test_confirm(self, db, runner):
        # Before running the command
        actual = db.engine.table_names()
        expected = [
            'state_contributions',
            'top_by_state_and_month',
            'top_by_state_and_year'
        ]
        assert actual == expected

        # After running the command
        result = runner.invoke(args=['database', 'drop'], input='y')
        actual = db.engine.table_names()
        expected = []
        assert actual == expected
        assert 'All tables were dropped' in result.output

    def test_abort(self, db, runner):
        # Before running the command
        actual = db.engine.table_names()
        expected = [
            'state_contributions',
            'top_by_state_and_month',
            'top_by_state_and_year'
        ]
        assert actual == expected

        # After running the command
        result = runner.invoke(args=['database', 'drop'], input='N')
        actual = db.engine.table_names()
        assert 'Aborted!' in result.output
        assert actual == expected
