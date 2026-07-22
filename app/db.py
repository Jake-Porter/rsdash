import sqlite3
from pathlib import Path

from app import config

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_conn() -> sqlite3.Connection:
    Path(config.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_conn()
    try:
        conn.executescript(SCHEMA_PATH.read_text())
        conn.commit()
    finally:
        conn.close()


def get_or_create_account(game: str, rsn: str) -> int:
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT id FROM accounts WHERE game=? AND rsn=?", (game, rsn)
        ).fetchone()
        if row:
            return row["id"]
        cur = conn.execute(
            "INSERT INTO accounts(game, rsn) VALUES (?, ?)", (game, rsn)
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_account_id(game: str, rsn: str) -> int | None:
    if not rsn:
        return None
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT id FROM accounts WHERE game=? AND rsn=?", (game, rsn)
        ).fetchone()
        return row["id"] if row else None
    finally:
        conn.close()
