"""
Verktøy for å opprette skjema og synkronisere demo-data.
"""

import ast
import re
import sqlite3
from pathlib import Path

from db import get_connection

ROOT = Path(__file__).resolve().parent.parent

STARTUP_SCRIPTS = [
    "sql/create_tables.sql",
]

DATA_SCRIPTS = [
    "sql/insert_data.sql",
    "sql/extra_data.sql",
]

PRE_BOOKING_SYNC_ORDER = [
    "Fasilitet",
    "Senter",
    "Idrettslag",
    "Profil",
    "Aktivitet",
    "har_fasilitet",
    "Bemanning",
    "Sal",
    "Tredemølle",
    "Sykkel",
    "Gruppe",
    "er_medlem",
    "Idrettslagstime",
    "møter_til_idrett",
    "Gruppeaktivitet",
]

POST_BOOKING_SYNC_ORDER = [
    "møter_til_gruppe",
    "Prikk",
]


def _table_exists(con, table_name):
    row = con.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _read_script(script_path):
    return (ROOT / script_path).read_text(encoding="utf-8")


def _ensure_migrations_table(con):
    con.executescript(
        "CREATE TABLE IF NOT EXISTS _migrations "
        "(script TEXT PRIMARY KEY, ran_at TEXT DEFAULT (datetime('now')));"
    )


def _mark_script_as_run(con, script):
    con.execute(
        "INSERT OR REPLACE INTO _migrations (script, ran_at) VALUES (?, datetime('now'))",
        (script,),
    )


def _table_columns(con, table_name):
    rows = con.execute(f'PRAGMA table_info("{table_name}")').fetchall()
    return [row[1] for row in rows]


def _primary_key_columns(con, table_name):
    rows = con.execute(f'PRAGMA table_info("{table_name}")').fetchall()
    return [row[1] for row in sorted(rows, key=lambda row: row[5]) if row[5] > 0]


def _split_insert_rows(script_text, table_name):
    pattern = re.compile(
        rf"INSERT INTO {re.escape(table_name)}\s*\((?P<columns>.*?)\)\s*VALUES\s*(?P<values>.*?);",
        re.S,
    )
    match = pattern.search(script_text)
    if match is None:
        return script_text, [], ""

    values_text = re.sub(r"--.*", "", match.group("values"))
    rows = ast.literal_eval("[" + values_text.strip() + "]")
    return script_text[:match.start()], list(rows), script_text[match.end():]


def _insert_booking_row(con, booking):
    senter_id, sal_id, gruppeaktivitet_id, profil_id, pamelding_nummer = booking
    exists = con.execute(
        """
        SELECT 1
        FROM påmeldt_til
        WHERE senter_ID = ? AND sal_ID = ? AND gruppeaktivitet_ID = ? AND profil_ID = ?
        """,
        (senter_id, sal_id, gruppeaktivitet_id, profil_id),
    ).fetchone()
    if exists is not None:
        return False

    occupied = con.execute(
        """
        SELECT 1
        FROM påmeldt_til
        WHERE senter_ID = ? AND sal_ID = ? AND gruppeaktivitet_ID = ? AND påmelding_nummer = ?
        """,
        (senter_id, sal_id, gruppeaktivitet_id, pamelding_nummer),
    ).fetchone()
    if occupied is not None:
        pamelding_nummer = con.execute(
            """
            SELECT COALESCE(MAX(påmelding_nummer), 0) + 1
            FROM påmeldt_til
            WHERE senter_ID = ? AND sal_ID = ? AND gruppeaktivitet_ID = ?
            """,
            (senter_id, sal_id, gruppeaktivitet_id),
        ).fetchone()[0]

    con.execute(
        """
        INSERT INTO påmeldt_til
            (senter_ID, sal_ID, gruppeaktivitet_ID, profil_ID, påmelding_nummer)
        VALUES (?, ?, ?, ?, ?)
        """,
        (senter_id, sal_id, gruppeaktivitet_id, profil_id, pamelding_nummer),
    )
    return True


def build_demo_source():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(_read_script(STARTUP_SCRIPTS[0]))

    for script in DATA_SCRIPTS:
        before_bookings, booking_rows, after_bookings = _split_insert_rows(
            _read_script(script),
            "påmeldt_til",
        )
        con.executescript(before_bookings)
        for booking in booking_rows:
            _insert_booking_row(con, booking)
        con.executescript(after_bookings)

    con.commit()
    return con


def _sync_missing_rows(target, source, table_name):
    columns = _table_columns(source, table_name)
    key_columns = _primary_key_columns(source, table_name)
    quoted_columns = ", ".join(f'"{col}"' for col in columns)
    insert_columns = ", ".join(f'"{col}"' for col in columns)
    exists_sql = (
        f'SELECT 1 FROM "{table_name}" WHERE '
        + " AND ".join(f'"{col}" = ?' for col in key_columns)
    )
    insert_sql = (
        f'INSERT INTO "{table_name}" ({insert_columns}) '
        f'VALUES ({", ".join("?" for _ in columns)})'
    )
    select_sql = f'SELECT {quoted_columns} FROM "{table_name}"'

    inserted = 0
    for row in source.execute(select_sql):
        key_values = tuple(row[col] for col in key_columns)
        if target.execute(exists_sql, key_values).fetchone() is not None:
            continue
        target.execute(insert_sql, tuple(row[col] for col in columns))
        inserted += 1
    return inserted


def _sync_bookings(target, source):
    inserted = 0
    for row in source.execute(
        """
        SELECT senter_ID, sal_ID, gruppeaktivitet_ID, profil_ID, påmelding_nummer
        FROM påmeldt_til
        ORDER BY senter_ID, sal_ID, gruppeaktivitet_ID, påmelding_nummer
        """
    ):
        inserted += int(_insert_booking_row(target, tuple(row)))
    return inserted


def run_startup_scripts(vis_status=False):
    con = get_connection()
    _ensure_migrations_table(con)
    if not _table_exists(con, "Fasilitet"):
        if vis_status:
            print(f"Kjører {STARTUP_SCRIPTS[0]} ...")
        con.executescript(_read_script(STARTUP_SCRIPTS[0]))
        if vis_status:
            print(f"OK: {STARTUP_SCRIPTS[0]}")
    elif vis_status:
        print("Fant eksisterende skjema. Hopper over opprettelse av tabeller.")

    _mark_script_as_run(con, STARTUP_SCRIPTS[0])
    con.commit()
    con.close()


def sync_demo_data(vis_status=False):
    run_startup_scripts(vis_status=vis_status)

    source = build_demo_source()
    target = get_connection()
    _ensure_migrations_table(target)

    total_inserted = 0
    try:
        for table_name in PRE_BOOKING_SYNC_ORDER:
            inserted = _sync_missing_rows(target, source, table_name)
            total_inserted += inserted
            if vis_status:
                print(f"{table_name}: la til {inserted} manglende rader.")

        booking_inserted = _sync_bookings(target, source)
        total_inserted += booking_inserted
        if vis_status:
            print(f"påmeldt_til: la til {booking_inserted} manglende rader.")

        for table_name in POST_BOOKING_SYNC_ORDER:
            inserted = _sync_missing_rows(target, source, table_name)
            total_inserted += inserted
            if vis_status:
                print(f"{table_name}: la til {inserted} manglende rader.")

        for script in DATA_SCRIPTS:
            _mark_script_as_run(target, script)
        target.commit()
    finally:
        source.close()
        target.close()

    if vis_status:
        print(f"Ferdig. La til totalt {total_inserted} manglende rader.")
