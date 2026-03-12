"""
main.py - TreningDB terminalmeny

Kjør:
    python python/main.py
"""

from use_case_2 import book_trening
from use_case_3 import registrer_oppmote
from use_case_4 import ukeplan
from use_case_5 import personlig_besokshistorie
from use_case_6 import svarteliste
from db import get_connection


def meny():
    print("\n=== TreningDB ===")
    print("Velg et alternativ:")
    print("0: Avslutt")
    print("1. Legg inn data (SQL-script)")
    print("2. Book trening")
    print("3. Registrer oppmøte")
    print("4. Ukeplan")
    print("5. Personlig besøkshistorie")
    print("6. Svartelisting")
    print("7. Mest aktive bruker")
    print("8. Finn treningspartnere")
    print("0. Avslutt")

SQL_SCRIPTS = [
    "sql/create_tables.sql",
    "sql/insert_data.sql",
    "sql/extra_data.sql",
]


def run_sql_script():
    con = get_connection()
    con.executescript(
        "CREATE TABLE IF NOT EXISTS _migrations "
        "(script TEXT PRIMARY KEY, ran_at TEXT DEFAULT (datetime('now')));"
    )
    already_run = {
        row[0] for row in con.execute("SELECT script FROM _migrations").fetchall()
    }
    for script in SQL_SCRIPTS:
        if script not in already_run:
            con.executescript(open(script).read())
            con.execute("INSERT INTO _migrations (script) VALUES (?)", (script,))
            con.commit()
    con.close()

def main():
    run_sql_script()
    while True:
        meny()
        valg = input("Velg: ").strip()

        if valg == "0":
            print("Avslutter.")
            break

        elif valg == "1":
            print("Kjør: sqlite3 treningdb.sqlite '.read sql/insert_data.sql'")

        elif valg == "2":
            epost       = input("Epost: ").strip()
            aktivitet   = input("Aktivitet (f.eks. Spin60): ").strip()
            dato        = input("Dato (YYYY-MM-DD): ").strip()
            starttid    = input("Starttid (HH:MM): ").strip()
            senter_navn = input("Senter: ").strip()
            book_trening(epost, aktivitet, dato, starttid, senter_navn)

        elif valg == "3":
            epost       = input("Epost: ").strip()
            trening_id  = input("Trening ID: ").strip()
            registrer_oppmote(epost, trening_id)

        elif valg == "4":
            start_dag = input("Startdag (YYYY-MM-DD): ").strip()
            uke       = int(input("Uke: ").strip())
            ukeplan(start_dag, uke)

        elif valg == "5":
            epost       = input("Epost: ").strip()
            start_dato  = input("Startdato (YYYY-MM-DD): ").strip()
            personlig_besokshistorie(epost, start_dato)
        elif valg == "6":
            epost       = input("Epost: ").strip()
            svarteliste(epost)

        elif valg == "7":
            print("Brukstilfelle 7 er ikke implementert ennå.")

        elif valg == "8":
            print("Brukstilfelle 8 er ikke implementert ennå.")

        else:
            print("Ugyldig valg, prøv igjen.")


if __name__ == "__main__":
    main()
