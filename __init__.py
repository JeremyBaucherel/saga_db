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


class Process (Base):
    __tablename__ = u"process"

    processName = sqlalchemy.Column(StrippedUnicode(), primary_key=True, autoincrement=False)
    description = sqlalchemy.Column(StrippedUnicode())


class Version(Base):
    __tablename__ = u"version"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    version = sqlalchemy.Column(StrippedUnicode())
    target = sqlalchemy.Column(StrippedUnicode())
    date = sqlalchemy.Column(sqlalchemy.DateTime())
    description = sqlalchemy.Column(StrippedUnicode())


## BIBLIOTHEQUE ##

class Bibliotheque_Auteur(Base):
    __tablename__ = u"bibliotheque_author"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    name_author = sqlalchemy.Column(StrippedUnicode())

class AuteurBibliotheque(Base):
    __tablename__ = u"bibliotheque_author_book_list"

    id_book_list = sqlalchemy.Column(sqlalchemy.Integer(), sqlalchemy.ForeignKey("bibliotheque_book_list.id"), primary_key=True, autoincrement=True)
    id_author = sqlalchemy.Column(sqlalchemy.Integer(), sqlalchemy.ForeignKey("bibliotheque_author.id"), primary_key=True, autoincrement=True)

class Bibliotheque(Base):
    __tablename__ = u"bibliotheque_book_list"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    id_categorie = sqlalchemy.Column(sqlalchemy.Integer(), sqlalchemy.ForeignKey("bibliotheque_categorie.id"))
    id_saga = sqlalchemy.Column(sqlalchemy.Integer(), sqlalchemy.ForeignKey("bibliotheque_saga.id"))
    number = sqlalchemy.Column(StrippedUnicode())
    name = sqlalchemy.Column(StrippedUnicode())
    id_book_publishing = sqlalchemy.Column(sqlalchemy.Integer(), sqlalchemy.ForeignKey("bibliotheque_book_publishing.id"))
    id_owner = sqlalchemy.Column(sqlalchemy.Integer(), sqlalchemy.ForeignKey("bibliotheque_owner.id"))
    id_location = sqlalchemy.Column(sqlalchemy.Integer(), sqlalchemy.ForeignKey("bibliotheque_location.id"))

    Bibliotheque_Categorie = sqlalchemy.orm.relation("Bibliotheque_Categorie", lazy='joined')
    Bibliotheque_Saga = sqlalchemy.orm.relation("Bibliotheque_Saga", lazy='joined')
    Bibliotheque_MaisonEdition = sqlalchemy.orm.relation("Bibliotheque_MaisonEdition", lazy='joined')
    Bibliotheque_Proprietaire = sqlalchemy.orm.relation("Bibliotheque_Proprietaire", lazy='joined')
    Bibliotheque_Emplacement = sqlalchemy.orm.relation("Bibliotheque_Emplacement", lazy='joined')

class Bibliotheque_Categorie(Base):
    __tablename__ = u"bibliotheque_categorie"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    name_categorie = sqlalchemy.Column(StrippedUnicode())

class Bibliotheque_Saga(Base):
    __tablename__ = u"bibliotheque_saga"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    name_saga = sqlalchemy.Column(StrippedUnicode())

class Bibliotheque_MaisonEdition(Base):
    __tablename__ = u"bibliotheque_book_publishing"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    name_book_publishing = sqlalchemy.Column(StrippedUnicode())

class Bibliotheque_Emplacement(Base):
    __tablename__ = u"bibliotheque_location"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    name_location = sqlalchemy.Column(StrippedUnicode())  

class Bibliotheque_Emprunteur(Base):
    __tablename__ = u"bibliotheque_borrower"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    id_book_list = sqlalchemy.Column(sqlalchemy.Integer(), sqlalchemy.ForeignKey("bibliotheque_book_list.id"))
    borrower = sqlalchemy.Column(StrippedUnicode()) 
    borrowing_date = sqlalchemy.Column(sqlalchemy.DateTime())

class Bibliotheque_Job(Base):
    __tablename__ = u"bibliotheque_job"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    name_job = sqlalchemy.Column(StrippedUnicode())  

class Bibliotheque_JobAuteur(Base):
    __tablename__ = u"bibliotheque_job_author"

    id_job = sqlalchemy.Column(sqlalchemy.Integer(), sqlalchemy.ForeignKey("bibliotheque_job.id"), primary_key=True)
    id_author = sqlalchemy.Column(sqlalchemy.Integer(), sqlalchemy.ForeignKey("bibliotheque_author.id"), primary_key=True) 

class Bibliotheque_Proprietaire(Base):
    __tablename__ = u"bibliotheque_owner"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    name_owner = sqlalchemy.Column(StrippedUnicode())  


## BLURAY ##

class Bluray(Base):
    __tablename__ = u"bluray"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    titre = sqlalchemy.Column(StrippedUnicode())
    id_categorie = sqlalchemy.Column(sqlalchemy.Integer(), sqlalchemy.ForeignKey("bluray_categorie.id"))
    id_saga = sqlalchemy.Column(sqlalchemy.Integer(), sqlalchemy.ForeignKey("bluray_saga.id"))
    number = sqlalchemy.Column(StrippedUnicode())
    steelbook = sqlalchemy.Column(sqlalchemy.Boolean())
    id_coffret = sqlalchemy.Column(sqlalchemy.Integer(), sqlalchemy.ForeignKey("bluray_coffret.id"))
    id_owner = sqlalchemy.Column(sqlalchemy.Integer(), sqlalchemy.ForeignKey("bluray_owner.id"))
    id_location = sqlalchemy.Column(sqlalchemy.Integer(), sqlalchemy.ForeignKey("bluray_location.id"))

    Bluray_Categorie = sqlalchemy.orm.relation("Bluray_Categorie", lazy='joined')
    Bluray_Saga = sqlalchemy.orm.relation("Bluray_Saga", lazy='joined')
    Bluray_Coffret = sqlalchemy.orm.relation("Bluray_Coffret", lazy='joined')
    Bluray_Proprietaire = sqlalchemy.orm.relation("Bluray_Proprietaire", lazy='joined')
    Bluray_Emplacement = sqlalchemy.orm.relation("Bluray_Emplacement", lazy='joined')

class Bluray_Coffret(Base):
    __tablename__ = u"bluray_coffret"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    name_coffret = sqlalchemy.Column(StrippedUnicode())


class Bluray_Categorie(Base):
    __tablename__ = u"bluray_categorie"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    name_categorie = sqlalchemy.Column(StrippedUnicode())

class Bluray_Saga(Base):
    __tablename__ = u"bluray_saga"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    name_saga = sqlalchemy.Column(StrippedUnicode())

class Bluray_Emplacement(Base):
    __tablename__ = u"bluray_location"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    name_location = sqlalchemy.Column(StrippedUnicode())  

class Bluray_Emprunteur(Base):
    __tablename__ = u"bluray_borrower"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    id_bluray = sqlalchemy.Column(sqlalchemy.Integer(), sqlalchemy.ForeignKey("bluray.id"))
    borrower = sqlalchemy.Column(StrippedUnicode()) 
    borrowing_date = sqlalchemy.Column(sqlalchemy.DateTime())

class Bluray_Proprietaire(Base):
    __tablename__ = u"bluray_owner"

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True, autoincrement=True)
    name_owner = sqlalchemy.Column(StrippedUnicode())  
