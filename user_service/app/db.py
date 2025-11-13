import sqlite3
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )
    db.commit()

    # On ne seed que si la table est vide
    cursor = db.execute("SELECT COUNT(*) AS n FROM users")
    n = cursor.fetchone()["n"]
    if n == 0:
        db.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("kilian", "123"),
        )
        db.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("bob", "456"),
        )
        db.commit()



def check_credentials(username: str, password: str) -> bool:
    db = get_db()
    row = db.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password),
    ).fetchone()
    return row is not None


def add_user(username: str, password: str):
    db = get_db()
    db.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, password),
    )
    db.commit()
