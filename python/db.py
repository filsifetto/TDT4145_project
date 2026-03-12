"""
db.py - felles databasetilkobling for alle brukstilfeller.

Bruk:
    from db import get_connection
    con = get_connection()
"""

import sqlite3
from pathlib import Path

# Databasefilen ligger i prosjektrooten
DB_PATH = Path(__file__).resolve().parent.parent / "treningdb.sqlite"


def get_connection() -> sqlite3.Connection:
    """Returnerer en tilkobling med foreign keys aktivert."""
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con
