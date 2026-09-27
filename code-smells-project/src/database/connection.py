import sqlite3

from flask import current_app, g


def connect(database_path, read_only=False):
    if read_only:
        conn = sqlite3.connect(f"file:{database_path}?mode=ro", uri=True)
    else:
        conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    if "db" not in g:
        g.db = connect(current_app.config["DATABASE_PATH"])
    return g.db


def get_read_only_db():
    if "db_ro" not in g:
        g.db_ro = connect(current_app.config["DATABASE_PATH"], read_only=True)
    return g.db_ro


def close_db(_exc=None):
    for key in ("db", "db_ro"):
        conn = g.pop(key, None)
        if conn is not None:
            conn.close()


def init_app(app):
    app.teardown_appcontext(close_db)
