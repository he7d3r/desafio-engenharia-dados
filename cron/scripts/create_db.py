#!/usr/bin/env python

"""Create an sqlite database with the appropriate tables

Usage:
    create_db [--db=<path>]
    create_db -h | --help

Options:
    -h --help           Show this screen.
    --db=<path>         The path to a file for the database
"""
import docopt
import os

from sqlalchemy import create_engine
from sqlalchemy import (BigInteger, Column, Date, Float, ForeignKey, Integer,
                        SmallInteger, String, Text)
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Import(Base):

    __tablename__ = 'import'

    CO_NCM = Column(Integer, ForeignKey('ncm.CO_NCM'), primary_key=True)
    CO_UNID = Column(SmallInteger, nullable=False)
    CO_PAIS = Column(SmallInteger, primary_key=True)
    SG_UF_NCM = Column(String(2), ForeignKey('uf.SG_UF'), primary_key=True)
    CO_VIA = Column(SmallInteger, primary_key=True)
    CO_URF = Column(Integer, primary_key=True)
    QT_ESTAT = Column(BigInteger, nullable=False)
    KG_LIQUIDO = Column(BigInteger, nullable=False)
    VL_FOB = Column(BigInteger, nullable=False)
    DATA = Column(Date, primary_key=True)

    def __init__(self, CO_NCM, CO_UNID, CO_PAIS, SG_UF_NCM, CO_VIA, CO_URF,
                 QT_ESTAT, KG_LIQUIDO, VL_FOB, DATA):
        self.CO_NCM = CO_NCM
        self.CO_UNID = CO_UNID
        self.CO_PAIS = CO_PAIS
        self.SG_UF_NCM = SG_UF_NCM
        self.CO_VIA = CO_VIA
        self.CO_URF = CO_URF
        self.QT_ESTAT = QT_ESTAT
        self.KG_LIQUIDO = KG_LIQUIDO
        self.VL_FOB = VL_FOB
        self.DATA = DATA


class Export(Base):

    __tablename__ = 'export'

    CO_NCM = Column(Integer, ForeignKey('ncm.CO_NCM'), primary_key=True)
    CO_UNID = Column(SmallInteger, nullable=False)
    CO_PAIS = Column(SmallInteger, primary_key=True)
    SG_UF_NCM = Column(String(2), ForeignKey('uf.SG_UF'), primary_key=True)
    CO_VIA = Column(SmallInteger, primary_key=True)
    CO_URF = Column(Integer, primary_key=True)
    QT_ESTAT = Column(BigInteger, nullable=False)
    KG_LIQUIDO = Column(BigInteger, nullable=False)
    VL_FOB = Column(BigInteger, nullable=False)
    DATA = Column(Date, primary_key=True)

    def __init__(self, CO_NCM, CO_UNID, CO_PAIS, SG_UF_NCM, CO_VIA, CO_URF,
                 QT_ESTAT, KG_LIQUIDO, VL_FOB, DATA):
        self.CO_NCM = CO_NCM
        self.CO_UNID = CO_UNID
        self.CO_PAIS = CO_PAIS
        self.SG_UF_NCM = SG_UF_NCM
        self.CO_VIA = CO_VIA
        self.CO_URF = CO_URF
        self.QT_ESTAT = QT_ESTAT
        self.KG_LIQUIDO = KG_LIQUIDO
        self.VL_FOB = VL_FOB
        self.DATA = DATA


class Ncm(Base):

    __tablename__ = 'ncm'

    CO_NCM = Column(Integer, primary_key=True)
    CO_UNID = Column(SmallInteger, nullable=False)
    CO_SH6 = Column(Integer, nullable=False)
    CO_PPE = Column(SmallInteger, nullable=False)
    CO_PPI = Column(SmallInteger, nullable=False)
    CO_FAT_AGREG = Column(SmallInteger, nullable=False)
    CO_CUCI_ITEM = Column(SmallInteger, nullable=False)
    CO_CGCE_N3 = Column(SmallInteger, nullable=False)
    CO_SIIT = Column(SmallInteger, nullable=False)
    CO_ISIC_CLASSE = Column(SmallInteger, nullable=False)
    CO_EXP_SUBSET = Column(SmallInteger, nullable=False)
    NO_NCM_POR = Column(Text(344), nullable=False)
    NO_NCM_ESP = Column(String(255), nullable=False)
    NO_NCM_ING = Column(String(255), nullable=False)

    def __init__(self, CO_NCM, CO_UNID, CO_SH6, CO_PPE, CO_PPI, CO_FAT_AGREG,
                 CO_CUCI_ITEM, CO_CGCE_N3, CO_SIIT, CO_ISIC_CLASSE,
                 CO_EXP_SUBSET, NO_NCM_POR, NO_NCM_ESP, NO_NCM_ING):
        self.CO_NCM = CO_NCM
        self.CO_UNID = CO_UNID
        self.CO_SH6 = CO_SH6
        self.CO_PPE = CO_PPE
        self.CO_PPI = CO_PPI
        self.CO_FAT_AGREG = CO_FAT_AGREG
        self.CO_CUCI_ITEM = CO_CUCI_ITEM
        self.CO_CGCE_N3 = CO_CGCE_N3
        self.CO_SIIT = CO_SIIT
        self.CO_ISIC_CLASSE = CO_ISIC_CLASSE
        self.CO_EXP_SUBSET = CO_EXP_SUBSET
        self.NO_NCM_POR = NO_NCM_POR
        self.NO_NCM_ESP = NO_NCM_ESP
        self.NO_NCM_ING = NO_NCM_ING


class Uf(Base):

    __tablename__ = 'uf'

    CO_UF = Column(SmallInteger, nullable=False)
    SG_UF = Column(String(2), primary_key=True)
    NO_UF = Column(String(24), nullable=False)
    NO_REGIAO = Column(String(24), nullable=False)

    def __init__(self, CO_UF, SG_UF, NO_UF, NO_REGIAO):
        self.CO_UF = CO_UF
        self.SG_UF = SG_UF
        self.NO_UF = NO_UF
        self.NO_REGIAO = NO_REGIAO


class TopByStateAndYear(Base):

    __tablename__ = 'top_by_state_and_year'

    federative_unit = Column(String(2), ForeignKey('uf.SG_UF'),
                             primary_key=True)
    year = Column(SmallInteger, primary_key=True)
    kind = Column(String(6), primary_key=True)
    product = Column(Integer, ForeignKey('ncm.CO_NCM'), primary_key=True)
    total = Column(BigInteger, nullable=False)

    def __init__(self, federative_unit, year, kind, product, total):
        self.federative_unit = federative_unit
        self.year = year
        self.kind = kind
        self.product = product
        self.total = total


class TopByStateAndMonth(Base):

    __tablename__ = 'top_by_state_and_month'

    federative_unit = Column(String(2), ForeignKey('uf.SG_UF'),
                             primary_key=True)
    year = Column(SmallInteger, primary_key=True)
    month = Column(SmallInteger, primary_key=True)
    kind = Column(String(6), primary_key=True)
    product = Column(Integer, ForeignKey('ncm.CO_NCM'), primary_key=True)
    total = Column(BigInteger, nullable=False)

    def __init__(self, federative_unit, year, month, kind, product, total):
        self.federative_unit = federative_unit
        self.year = year
        self.month = month
        self.kind = kind
        self.product = product
        self.total = total


class StateContributions(Base):

    __tablename__ = 'state_contributions'

    kind = Column(String(6), primary_key=True)
    year = Column(SmallInteger, primary_key=True)
    federative_unit = Column(String(2), ForeignKey('uf.SG_UF'),
                             primary_key=True)
    total = Column(BigInteger, nullable=False)
    percentage = Column(Float, nullable=False)

    def __init__(self, kind, year, federative_unit, total, percentage):
        self.kind = kind
        self.year = year
        self.federative_unit = federative_unit
        self.total = total
        self.percentage = percentage


def create(database_url):
    engine = create_engine(database_url, echo=True)
    Base.metadata.create_all(engine)


def main(argv=None):

    args = docopt.docopt(__doc__, argv=argv)

    db_path = os.path.expanduser(args['--db'])
    database_url = f'sqlite:///{db_path}'

    create(database_url)


if __name__ == '__main__':
    main()
