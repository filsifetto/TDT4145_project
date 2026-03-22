"""
db.py – Felles databasetilkobling for TreningDB

Bruk:
    from db import get_connection
    con = get_connection()
"""

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "treningdb.sqlite"


def get_connection() -> sqlite3.Connection:
    """Returnerer en tilkobling med foreign keys aktivert."""
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con
