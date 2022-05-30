# -*- coding: iso-8859-1 -*-

import os.path
import sys


ROOT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(ROOT_PATH)

import math
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import sqlalchemy.ext.hybrid
import sqlalchemy.ext.associationproxy
import sqlalchemy.pool
import sqlalchemy.types
import urllib



def make_sql_session (odbc_driver, odbc_dsn):
    #engine = sqlalchemy.create_engine(config.DB_DSN, poolclass=sqlalchemy.pool.NullPool)
    dsn = "{}:///?odbc_connect={}".format(urllib.quote_plus(odbc_driver, odbc_dsn))
    engine = sqlalchemy.create_engine(dsn, poolclass=sqlalchemy.pool.NullPool, convert_unicode=True)
    db_session = sqlalchemy.orm.sessionmaker(bind=engine)()

    return db_session

def lock_table (db_con, table_name):
    db_con.execute("sp_tableoption {}, 'table lock on bulk load', 1".format(table_name))

def unlock_table (db_con, table_name):
    db_con.execute("sp_tableoption {}, 'table lock on bulk load', 0".format(table_name))

Base = sqlalchemy.ext.declarative.declarative_base()


class StrippedUnicode(sqlalchemy.types.TypeDecorator):
    impl = sqlalchemy.types.UnicodeText
    cache_ok = True
    
    def process_result_value(self, value, dialect):
        "Strip the trailing spaces on resulting values"
        if value:
            return value.rstrip()
        return None

    def copy(self):
        "Make a copy of this type"
        return StrippedUnicode(self.impl.length)


class SqlDictQuery (object):
    def __init__ (self, query, entity_cls):
        self._query = query
        self._fieldnames = [col.name for col in entity_cls.__table__.columns]
        self._iter = iter(self._query)

    def __iter__ (self):
        return self

    def next (self):
        sql_row = self._iter.next()
        row = {}
        for column_name in self._fieldnames:
            row[column_name] = getattr(sql_row, column_name)
        return row


class Utilisateur (Base):
    __tablename__ = u"users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    logon = sqlalchemy.Column(StrippedUnicode())
    nom = sqlalchemy.Column(StrippedUnicode())
    prenom = sqlalchemy.Column(StrippedUnicode())
    logonCirce = sqlalchemy.Column(StrippedUnicode())
    passwordCirce = sqlalchemy.Column(StrippedUnicode())
    dateChgtPwdCirce = sqlalchemy.Column(sqlalchemy.DateTime())
    mail = sqlalchemy.Column(StrippedUnicode())
    mdp = sqlalchemy.Column(StrippedUnicode())
    mdp_methode = sqlalchemy.Column(StrippedUnicode())
    mdp_token = sqlalchemy.Column(StrippedUnicode())
    session_id = sqlalchemy.Column(sqlalchemy.Unicode())
    action_date = sqlalchemy.Column(sqlalchemy.DateTime())
    rgpd_date = sqlalchemy.Column(sqlalchemy.DateTime())

class UtilisateurRole (Base):
    __tablename__ = u"users_role"

    id_users = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), primary_key=True, autoincrement=False)
    id_role = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("role.id"), primary_key=True, autoincrement=False)

class Autorisation (Base):
    __tablename__ = u"autorisation"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    nom = sqlalchemy.Column(StrippedUnicode())
    description = sqlalchemy.Column(StrippedUnicode())

class Role (Base):
    __tablename__ = u"role"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    nom = sqlalchemy.Column(StrippedUnicode())
    description = sqlalchemy.Column(StrippedUnicode())

class RoleAutorisation (Base):
    __tablename__ = u"role_autorisation"

    id_role = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("role.id"), primary_key=True, autoincrement=False)
    id_autorisation = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("autorisation.id"), primary_key=True, autoincrement=False)

    role = sqlalchemy.orm.relation("Role")
    autorisation = sqlalchemy.orm.relation("Autorisation")

class logExecution(Base):
    __tablename__ = u"logExecution"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    processName = sqlalchemy.Column(StrippedUnicode())
    dateExecution = sqlalchemy.Column(sqlalchemy.DateTime())
    statut = sqlalchemy.Column(StrippedUnicode())

class RoutingGTI (Base):
    __tablename__ = u"routingGTI"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    Gamme = sqlalchemy.Column(StrippedUnicode())
    CptGrpGamme = sqlalchemy.Column(sqlalchemy.Integer()) 
    DescriptionSAP = sqlalchemy.Column(StrippedUnicode())
    PGM = sqlalchemy.Column(StrippedUnicode())
    PA_TC = sqlalchemy.Column(StrippedUnicode())

class Process (Base):
    __tablename__ = u"process"

    processName = sqlalchemy.Column(StrippedUnicode(), primary_key=True, autoincrement=False)
    description = sqlalchemy.Column(StrippedUnicode())


class ProcessRoutingGTI (Base):
    __tablename__ = u"process_routingGTI"

    id_routingGTI = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("routingGTI.id"), primary_key=True, autoincrement=False)
    processName = sqlalchemy.Column(StrippedUnicode(), sqlalchemy.ForeignKey("process.processName"), primary_key=True, autoincrement=False)
    id_statut = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("statutDep.id"))

    routingGTI = sqlalchemy.orm.relation("RoutingGTI")
    process = sqlalchemy.orm.relation("Process")
    statut = sqlalchemy.orm.relation("StatutDep")


class UsersRoutingGTI(Base):
    __tablename__ = u"users_routingGTI"

    id_users = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), primary_key=True, autoincrement=False)
    id_routingGTI = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("routingGTI.id"), primary_key=True, autoincrement=False)

    users = sqlalchemy.orm.relation("Utilisateur")
    routingGTI = sqlalchemy.orm.relation("RoutingGTI")


class ParamComs(Base):
    __tablename__ = u"paramComs"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    Gamme = sqlalchemy.Column(StrippedUnicode())
    Operation = sqlalchemy.Column(sqlalchemy.Integer())
    MP = sqlalchemy.Column(StrippedUnicode())
    Equation = sqlalchemy.Column(StrippedUnicode())
    First_MSN = sqlalchemy.Column(sqlalchemy.Integer())
    Last_MSN = sqlalchemy.Column(sqlalchemy.Integer())
    Effectivity = sqlalchemy.Column(StrippedUnicode())
    Effectivity_concat = sqlalchemy.Column(StrippedUnicode())


class ParamGTI(Base):
    __tablename__ = u"paramGTI"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    id_routingGTI = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("routingGTI.id"))
    GTI = sqlalchemy.Column(StrippedUnicode())
    DocType = sqlalchemy.Column(StrippedUnicode())
    Part = sqlalchemy.Column(sqlalchemy.Integer())
    Gamme = sqlalchemy.Column(StrippedUnicode())
    cptGrGam = sqlalchemy.Column(sqlalchemy.Integer())
    Operation = sqlalchemy.Column(sqlalchemy.Integer())
    creationStatut = sqlalchemy.Column(sqlalchemy.Boolean())
    nbDigitMsnSap = sqlalchemy.Column(sqlalchemy.Integer())
    groupeGestionnaire = sqlalchemy.Column(StrippedUnicode())
    DesignationsCSV = sqlalchemy.Column(StrippedUnicode())
    Section = sqlalchemy.Column(StrippedUnicode())
    processName = sqlalchemy.Column(StrippedUnicode())
    Libelle = sqlalchemy.Column(StrippedUnicode())
    NumDocMsn = sqlalchemy.Column(sqlalchemy.Integer())
    pvnameCSV = sqlalchemy.Column(StrippedUnicode())
    pvnamePDF = sqlalchemy.Column(StrippedUnicode())
    folderpv = sqlalchemy.Column(StrippedUnicode())
    Zone = sqlalchemy.Column(StrippedUnicode())
    Langue = sqlalchemy.Column(StrippedUnicode())
    LongTitle = sqlalchemy.Column(StrippedUnicode())
    ShortTitle = sqlalchemy.Column(StrippedUnicode())


class ParamMetalFullConf_A320(Base):
    __tablename__ = u"paramMetalFullConf_A320"

    NumPoint = sqlalchemy.Column("NumPoint", StrippedUnicode(),  primary_key=True, autoincrement=False)
    Fin = sqlalchemy.Column("Fin", StrippedUnicode())
    NumExigGTR = sqlalchemy.Column("NumExigGTR", StrippedUnicode())
    Designation_FR = sqlalchemy.Column("Designation_FR", StrippedUnicode())
    Designation_EN = sqlalchemy.Column("Designation_EN", StrippedUnicode())
    Location_FR = sqlalchemy.Column("Location_FR", StrippedUnicode())
    Location_EN = sqlalchemy.Column("Location_EN", StrippedUnicode())
    I = sqlalchemy.Column("I", sqlalchemy.Integer())
    PtMesureA_FR = sqlalchemy.Column("PtMesureA_FR", StrippedUnicode())
    PtMesureA_EN = sqlalchemy.Column("PtMesureA_EN", StrippedUnicode())
    PtMesureB_FR = sqlalchemy.Column("PtMesureB_FR", StrippedUnicode())
    PtMesureB_EN = sqlalchemy.Column("PtMesureB_EN", StrippedUnicode())
    PriseEQT = sqlalchemy.Column("PriseEQT", StrippedUnicode())
    ValMax = sqlalchemy.Column("ValMax", sqlalchemy.Integer())
    ValMaxRel = sqlalchemy.Column("ValMaxRel", StrippedUnicode())
    DateMarqueOp = sqlalchemy.Column("DateMarqueOp", StrippedUnicode())
    Observations = sqlalchemy.Column("Observations", StrippedUnicode())
    FinPlus = sqlalchemy.Column("FinPlus", StrippedUnicode())
    CaPlus = sqlalchemy.Column("CaPlus", StrippedUnicode())
    RfPlus = sqlalchemy.Column("RfPlus", StrippedUnicode())
    DsPlus = sqlalchemy.Column("DsPlus", StrippedUnicode())
    StdPlus = sqlalchemy.Column("StdPlus", StrippedUnicode())
    VersionPlus = sqlalchemy.Column("VersionPlus", StrippedUnicode())
    FinMoins = sqlalchemy.Column("FinMoins", StrippedUnicode())
    CaMoins = sqlalchemy.Column("CaMoins", StrippedUnicode())
    RfMoins = sqlalchemy.Column("RfMoins", StrippedUnicode())
    DsMoins = sqlalchemy.Column("DsMoins", StrippedUnicode())
    StdMoins = sqlalchemy.Column("StdMoins", StrippedUnicode())
    VersionMoins = sqlalchemy.Column("VersionMoins", StrippedUnicode())
    ComposantPlus = sqlalchemy.Column("ComposantPlus", StrippedUnicode())
    QuantitePlus = sqlalchemy.Column("QuantitePlus", StrippedUnicode())
    PvZone = sqlalchemy.Column("PvZone", StrippedUnicode())
    ClassementPoints = sqlalchemy.Column("ClassementPoints", StrippedUnicode())
    TypePoint = sqlalchemy.Column("TypePoint", StrippedUnicode())


class ParamPFE(Base):
    __tablename__ = u"paramPFE"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    id_routingGTI = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("routingGTI.id"))
    pgm = sqlalchemy.Column(StrippedUnicode())
    gamme = sqlalchemy.Column(StrippedUnicode())
    cptGrGam = sqlalchemy.Column(sqlalchemy.Integer())   
    stations = sqlalchemy.Column(StrippedUnicode())
    deltaJour = sqlalchemy.Column(sqlalchemy.Integer())
    ecartDateCalcul = sqlalchemy.Column(sqlalchemy.Integer())
    alerteDatePrepa = sqlalchemy.Column(sqlalchemy.Integer())



class ParamTrag_TypeCable(Base):
    __tablename__ = u"paramTrag_TypeCable"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    code = sqlalchemy.Column(StrippedUnicode())
    construction = sqlalchemy.Column(StrippedUnicode())
    description = sqlalchemy.Column(StrippedUnicode())
    norme = sqlalchemy.Column(StrippedUnicode())
    processName = sqlalchemy.Column(StrippedUnicode())


class ParamTrag_TypePin(Base):
    __tablename__ = u"paramTrag_TypePin"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    typePin = sqlalchemy.Column(StrippedUnicode())
    description = sqlalchemy.Column(StrippedUnicode())
    norme = sqlalchemy.Column(StrippedUnicode())


class Pgm(Base):
    __tablename__ = u"pgm"

    pgm = sqlalchemy.Column(StrippedUnicode(), primary_key=True, autoincrement=False)


class ProcessCirce(Base):
    __tablename__ = u"processCirce"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    pgm = sqlalchemy.Column(StrippedUnicode())
    msn = sqlalchemy.Column(sqlalchemy.Integer())
    numRequestCirce = sqlalchemy.Column(sqlalchemy.Integer())
    dateRequestCirce = sqlalchemy.Column(sqlalchemy.DateTime())
    loginCirceRequestor = sqlalchemy.Column(StrippedUnicode())
    loginWindowsRequestor = sqlalchemy.Column(StrippedUnicode())
    numCirceTreatment = sqlalchemy.Column(StrippedUnicode())
    dateCirceTreatment = sqlalchemy.Column(sqlalchemy.DateTime())
    dateRecupCirceTreatment = sqlalchemy.Column(sqlalchemy.DateTime())


class ProcessPV(Base):
    __tablename__ = u"processPV"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    id_routingGTI = sqlalchemy.Column(sqlalchemy.Integer(), sqlalchemy.ForeignKey("routingGTI.id"))
    pgm = sqlalchemy.Column(StrippedUnicode(), sqlalchemy.ForeignKey("pgm.pgm"))
    msn = sqlalchemy.Column(sqlalchemy.Integer())
    gamme = sqlalchemy.Column(StrippedUnicode())
    cptGrGam = sqlalchemy.Column(sqlalchemy.Integer())
    prepaSap = sqlalchemy.Column(sqlalchemy.Boolean())
    ordreFabrication = sqlalchemy.Column(StrippedUnicode())
    prepaPV = sqlalchemy.Column(sqlalchemy.Boolean())
    prepaPdf = sqlalchemy.Column(sqlalchemy.Boolean())
    majSap = sqlalchemy.Column(sqlalchemy.Boolean())
    datePrepaSap = sqlalchemy.Column(sqlalchemy.DateTime())
    dateAddOf = sqlalchemy.Column(sqlalchemy.DateTime())
    dateMajPV = sqlalchemy.Column(sqlalchemy.DateTime())
    dateEntreeStation = sqlalchemy.Column(sqlalchemy.DateTime())
    statutScript = sqlalchemy.Column(StrippedUnicode())


class StatutDep(Base):
    __tablename__ = u"statutDep"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    statut = sqlalchemy.Column(StrippedUnicode())

class Version(Base):
    __tablename__ = u"version"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    version = sqlalchemy.Column(StrippedUnicode())
    target = sqlalchemy.Column(StrippedUnicode())
    date = sqlalchemy.Column(sqlalchemy.DateTime())
    description = sqlalchemy.Column(StrippedUnicode())

class ParamOther(Base):
    __tablename__ = u"paramOther"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    processName = sqlalchemy.Column(StrippedUnicode())
    categorie = sqlalchemy.Column(StrippedUnicode())
    nom = sqlalchemy.Column(StrippedUnicode())
    valeur = sqlalchemy.Column(StrippedUnicode())
    description = sqlalchemy.Column(StrippedUnicode())
    actif = sqlalchemy.Column(sqlalchemy.Boolean())
