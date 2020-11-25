from src.database import db


class TopByStateAndYear(db.Model):

    state_code = db.Column(db.String(2), primary_key=True)
    state = db.Column(db.String(24), nullable=False)
    year = db.Column(db.SmallInteger, primary_key=True)
    kind = db.Column(db.String(6), primary_key=True)
    product_code = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.VARCHAR(344), nullable=False)
    total = db.Column(db.BigInteger, nullable=False)


class TopByStateAndMonth(db.Model):

    state_code = db.Column(db.String(2), primary_key=True)
    state = db.Column(db.String(24), nullable=False)
    year = db.Column(db.SmallInteger, primary_key=True)
    month = db.Column(db.SmallInteger, primary_key=True)
    kind = db.Column(db.String(6), primary_key=True)
    product_code = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.VARCHAR(344), nullable=False)
    total = db.Column(db.BigInteger, nullable=False)


class StateContributions(db.Model):

    kind = db.Column(db.String(6), primary_key=True)
    year = db.Column(db.SmallInteger, primary_key=True)
    state_code = db.Column(db.String(2), primary_key=True)
    state = db.Column(db.String(24), nullable=False)
    total = db.Column(db.BigInteger, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
