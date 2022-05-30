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
