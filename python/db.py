"""
db.py - felles databasetilkobling for alle brukstilfeller.

Bruk:
    from db import get_connection
    con = get_connection()
"""

import sqlite3
from pathlib import Path

# Databasefilen ligger i prosjektrooten
ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "treningdb.sqlite"
MIGRATIONS_DIR = ROOT / "sql" / "migrations"
PAMELDT_TIL_MIGRATION_PATH = MIGRATIONS_DIR / "001_pamelding_nummer.sql"


def _table_exists(con: sqlite3.Connection, table_name: str) -> bool:
    row = con.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _pamelding_nummer_er_modernisert(con: sqlite3.Connection) -> bool:
    if not _table_exists(con, "påmeldt_til"):
        return True

    broken_refs = con.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE sql LIKE '%påmeldt_til_gammel%'
        LIMIT 1
        """
    ).fetchone()
    if broken_refs is not None:
        return False

    rows = con.execute("PRAGMA table_info('påmeldt_til')").fetchall()
    for row in rows:
        navn = row[1]
        not_null = row[3]
        if navn == "påmelding_nummer":
            return not_null == 0
    return True


def _oppgrader_pamelding_nummer(con: sqlite3.Connection) -> None:
    if _pamelding_nummer_er_modernisert(con):
        return

    migration_sql = PAMELDT_TIL_MIGRATION_PATH.read_text(encoding="utf-8")
    con.execute("PRAGMA foreign_keys = OFF")
    try:
        con.executescript(migration_sql)
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.execute("PRAGMA foreign_keys = ON")


def get_connection() -> sqlite3.Connection:
    """Returnerer en tilkobling med foreign keys aktivert."""
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    _oppgrader_pamelding_nummer(con)
    return con
