from src.database import db


class Import(db.Model):

    CO_NCM = db.Column(db.Integer, db.ForeignKey('ncm.CO_NCM'),
                       primary_key=True)
    CO_UNID = db.Column(db.SmallInteger, nullable=False)
    CO_PAIS = db.Column(db.SmallInteger, primary_key=True)
    SG_UF_NCM = db.Column(db.String(2), db.ForeignKey('uf.SG_UF'),
                          primary_key=True)
    CO_VIA = db.Column(db.SmallInteger, primary_key=True)
    CO_URF = db.Column(db.Integer, primary_key=True)
    QT_ESTAT = db.Column(db.BigInteger, nullable=False)
    KG_LIQUIDO = db.Column(db.BigInteger, nullable=False)
    VL_FOB = db.Column(db.BigInteger, nullable=False)
    DATA = db.Column(db.Date, primary_key=True)


class Export(db.Model):

    CO_NCM = db.Column(db.Integer, db.ForeignKey('ncm.CO_NCM'),
                       primary_key=True)
    CO_UNID = db.Column(db.SmallInteger, nullable=False)
    CO_PAIS = db.Column(db.SmallInteger, primary_key=True)
    SG_UF_NCM = db.Column(db.String(2), db.ForeignKey('uf.SG_UF'),
                          primary_key=True)
    CO_VIA = db.Column(db.SmallInteger, primary_key=True)
    CO_URF = db.Column(db.Integer, primary_key=True)
    QT_ESTAT = db.Column(db.BigInteger, nullable=False)
    KG_LIQUIDO = db.Column(db.BigInteger, nullable=False)
    VL_FOB = db.Column(db.BigInteger, nullable=False)
    DATA = db.Column(db.Date, primary_key=True)


class Ncm(db.Model):

    CO_NCM = db.Column(db.Integer, primary_key=True)
    CO_UNID = db.Column(db.SmallInteger, nullable=False)
    CO_SH6 = db.Column(db.Integer, nullable=False)
    CO_PPE = db.Column(db.SmallInteger, nullable=False)
    CO_PPI = db.Column(db.SmallInteger, nullable=False)
    CO_FAT_AGREG = db.Column(db.SmallInteger, nullable=False)
    CO_CUCI_ITEM = db.Column(db.Integer, nullable=False)
    CO_CGCE_N3 = db.Column(db.SmallInteger, nullable=False)
    CO_SIIT = db.Column(db.SmallInteger, nullable=False)
    CO_ISIC_CLASSE = db.Column(db.SmallInteger, nullable=False)
    CO_EXP_SUBSET = db.Column(db.SmallInteger, nullable=False)
    NO_NCM_POR = db.Column(db.VARCHAR(344), nullable=False)
    NO_NCM_ESP = db.Column(db.String(255), nullable=False)
    NO_NCM_ING = db.Column(db.String(255), nullable=False)


class Uf(db.Model):

    CO_UF = db.Column(db.SmallInteger, nullable=False)
    SG_UF = db.Column(db.String(2), primary_key=True)
    NO_UF = db.Column(db.String(24), nullable=False)
    NO_REGIAO = db.Column(db.String(24), nullable=False)


class TopByStateAndYear(db.Model):

    federative_unit = db.Column(db.String(2), db.ForeignKey('uf.SG_UF'),
                                primary_key=True)
    year = db.Column(db.SmallInteger, primary_key=True)
    kind = db.Column(db.String(6), primary_key=True)
    product = db.Column(db.Integer, db.ForeignKey('ncm.CO_NCM'),
                        primary_key=True)
    total = db.Column(db.BigInteger, nullable=False)


class TopByStateAndMonth(db.Model):

    federative_unit = db.Column(db.String(2), db.ForeignKey('uf.SG_UF'),
                                primary_key=True)
    year = db.Column(db.SmallInteger, primary_key=True)
    month = db.Column(db.SmallInteger, primary_key=True)
    kind = db.Column(db.String(6), primary_key=True)
    product = db.Column(db.Integer, db.ForeignKey('ncm.CO_NCM'),
                        primary_key=True)
    total = db.Column(db.BigInteger, nullable=False)


class StateContributions(db.Model):

    kind = db.Column(db.String(6), primary_key=True)
    year = db.Column(db.SmallInteger, primary_key=True)
    federative_unit = db.Column(db.String(2), db.ForeignKey('uf.SG_UF'),
                                primary_key=True)
    total = db.Column(db.BigInteger, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
