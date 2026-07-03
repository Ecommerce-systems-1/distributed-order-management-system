import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", ":memory:")

_conn: sqlite3.Connection | None = None


def init_db() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        if DB_PATH != ":memory:":
            os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
    return _conn


def get_db() -> sqlite3.Connection:
    return init_db()
