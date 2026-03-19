"""
main.py - TreningDB terminalmeny

Kjør:
    python python/main.py
"""

from data_sync import run_startup_scripts, sync_demo_data
from use_case_2 import book_trening
from use_case_3 import registrer_oppmote
from use_case_4 import ukeplan
from use_case_5 import personlig_besokshistorie
from use_case_6 import svarteliste
from use_case_7 import mest_aktive_bruker
from use_case_8 import finn_treningspartnere


def meny():
    print("\n=== TreningDB ===")
    print("Velg et alternativ:")
    print("1. Legg inn data (SQL-script)")
    print("2. Book trening")
    print("3. Registrer oppmøte")
    print("4. Ukeplan")
    print("5. Personlig besøkshistorie")
    print("6. Svartelisting")
    print("7. Mest aktive bruker")
    print("8. Finn treningspartnere")
    print("0. Avslutt")


def _kjor_menyalternativ(action):
    try:
        action()
    except SystemExit:
        pass
    except Exception as e:
        print(f"Uventet feil: {e}")


def main():
    run_startup_scripts()
    while True:
        meny()
        valg = input("Velg: ").strip()

        if valg == "0":
            print("Avslutter.")
            break

        elif valg == "1":
            _kjor_menyalternativ(lambda: sync_demo_data(vis_status=True))

        elif valg == "2":
            epost = input("Epost: ").strip()
            aktivitet = input("Aktivitet (f.eks. Spin60): ").strip()
            dato = input("Dato (YYYY-MM-DD): ").strip()
            starttid = input("Starttid (HH:MM): ").strip()
            senter_navn = input("Senter: ").strip()
            _kjor_menyalternativ(
                lambda: book_trening(epost, aktivitet, dato, starttid, senter_navn)
            )

        elif valg == "3":
            epost = input("Epost: ").strip()
            _kjor_menyalternativ(lambda: registrer_oppmote(epost))

        elif valg == "4":
            start_dag = input("Startdag (YYYY-MM-DD): ").strip()
            uke = int(input("Uke: ").strip())
            _kjor_menyalternativ(lambda: ukeplan(start_dag, uke))

        elif valg == "5":
            epost = input("Epost: ").strip()
            start_dato = input("Startdato (YYYY-MM-DD): ").strip()
            _kjor_menyalternativ(lambda: personlig_besokshistorie(epost, start_dato))

        elif valg == "6":
            epost = input("Epost: ").strip()
            _kjor_menyalternativ(lambda: svarteliste(epost))

        elif valg == "7":
            maaned = int(input("Måned (1-12): ").strip())
            _kjor_menyalternativ(lambda: mest_aktive_bruker(maaned))

        elif valg == "8":
            _kjor_menyalternativ(finn_treningspartnere)

        else:
            print("Ugyldig valg, prøv igjen.")


if __name__ == "__main__":
    main()
