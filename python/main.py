"""
main.py - TreningDB terminalmeny

Kjør:
    python python/main.py
"""

from use_case_2 import book_trening
from use_case_3 import registrer_oppmote
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

"""
kjører alle SQL-skriptene i sql/create_tables.sql og sql/insert_data.sql som ikke er allerede kjørt.
"""


def run_sql_script():
    con = get_connection()
    con.executescript(open("sql/create_tables.sql").read())
    con.executescript(open("sql/insert_data.sql").read())
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
            print("Brukstilfelle 4 er ikke implementert ennå.")

        elif valg == "5":
            print("Brukstilfelle 5 er ikke implementert ennå.")

        elif valg == "6":
            print("Brukstilfelle 6 er ikke implementert ennå.")

        elif valg == "7":
            print("Brukstilfelle 7 er ikke implementert ennå.")

        elif valg == "8":
            print("Brukstilfelle 8 er ikke implementert ennå.")

        else:
            print("Ugyldig valg, prøv igjen.")


if __name__ == "__main__":
    main()
