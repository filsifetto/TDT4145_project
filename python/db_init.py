"""
db_init.py – Databaseinitialisering for TreningDB

Kjører alle SQL-migrasjoner i sql/migrations/ som ikke allerede er
registrert i _migrations-tabellen (spores med navn og tidspunkt).

Migrasjoner kjøres i alfabetisk filrekkefølge, slik at nummerprefikset
(000_, 001_, ...) bestemmer rekkefølgen.  Filer som starter med '_'
hoppes over (brukes for arkiverte eller deaktiverte migrasjoner).

Bruk:
    from db_init import run_migrations
    run_migrations()           # stille initialisering
    run_migrations(verbose=True)  # vis fremgang i terminalen
"""

from pathlib import Path

from db import get_connection

ROOT = Path(__file__).resolve().parent.parent
MIGRATIONS_DIR = ROOT / "sql" / "migrations"


def _ensure_migrations_table(con) -> None:
    con.executescript(
        "CREATE TABLE IF NOT EXISTS _migrations "
        "(script TEXT PRIMARY KEY, ran_at TEXT DEFAULT (datetime('now')));"
    )
    con.commit()


def _already_ran(con, script_name: str) -> bool:
    return (
        con.execute(
            "SELECT 1 FROM _migrations WHERE script = ?", (script_name,)
        ).fetchone()
        is not None
    )


def _mark_as_ran(con, script_name: str) -> None:
    con.execute(
        "INSERT OR REPLACE INTO _migrations (script, ran_at) VALUES (?, datetime('now'))",
        (script_name,),
    )


def ensure_schema() -> None:
    """Oppretter tabeller og triggere (000_create_tables.sql) hvis de ikke finnes."""
    schema_file = MIGRATIONS_DIR / "000_create_tables.sql"
    con = get_connection()
    _ensure_migrations_table(con)
    if not _already_ran(con, schema_file.name):
        con.executescript(schema_file.read_text(encoding="utf-8"))
        _mark_as_ran(con, schema_file.name)
        con.commit()
    con.close()


def run_migrations(verbose: bool = False) -> None:
    """Kjører alle migrasjoner som ikke allerede er kjørt."""
    con = get_connection()
    _ensure_migrations_table(con)

    migration_files = sorted(
        f for f in MIGRATIONS_DIR.glob("*.sql") if not f.name.startswith("_")
    )

    ran_count = 0
    for path in migration_files:
        name = path.name
        if _already_ran(con, name):
            if verbose:
                print(f"  Hopper over {name} (allerede kjørt).")
            continue

        if verbose:
            print(f"  Kjører {name} ...")
        con.executescript(path.read_text(encoding="utf-8"))
        _mark_as_ran(con, name)
        con.commit()
        ran_count += 1
        if verbose:
            print(f"  OK: {name}")

    if verbose:
        if ran_count == 0:
            print("Alle migrasjoner er allerede kjørt – ingenting å gjøre.")
        else:
            print(f"Ferdig. Kjørte {ran_count} migrasjon(er).")

    con.close()
