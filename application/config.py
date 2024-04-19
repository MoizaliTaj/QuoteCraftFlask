import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class LocalDevelopmentConfig(Config):
    SQLITE_DB_DIR = os.path.join(basedir, "../db_directory/db")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "database.sqlite3")
    SQLALCHEMY_BINDS = {
        'quotes': "sqlite:///" + os.path.join(SQLITE_DB_DIR, "quotes.sqlite3"),
        'phone_book': "sqlite:///" + os.path.join(SQLITE_DB_DIR, "phone_book.sqlite3"),
        'logs': "sqlite:///" + os.path.join(SQLITE_DB_DIR, "logs.sqlite3"),
        'other': "sqlite:///" + os.path.join(SQLITE_DB_DIR, "other.sqlite3"),
    }
    DEBUG = True
