"""
6. Svartelisting. Brukeren ‘johnny@stud.ntnu.no’ fikk uheldigvis tre prikker i system
og skal utestenges fra elektronisk booking i 30 dager. Implementeres i Python og
SQL. Dere skal sjekke at det finnes minst tre prikker innen siste 30 dager før dere
svartelister.
"""

import sqlite3
import sys
from datetime import datetime, timedelta
from db import get_connection

# Parametere
EPOST = "johnny@stud.ntnu.no"


def antall_prikker_siste_maaned(epost: str) -> int:
    """Returnerer antall prikker brukeren har fått de siste 30 dagene."""
    con = get_connection()
    try:
        row = con.execute(
            "SELECT ID FROM Profil WHERE epost = :epost",
            {"epost": epost}
        ).fetchone()
        if row is None:
            raise ValueError(f"Bruker {epost} ikke funnet.")
        profil_id = row["ID"]

        start_dato = datetime.now() - timedelta(days=30)
        slutt_dato = datetime.now()

        return con.execute(
            "SELECT COUNT(*) FROM Prikk WHERE profil_ID = :profil_id AND dato BETWEEN :start_dato AND :slutt_dato",
            {"profil_id": profil_id, "start_dato": start_dato, "slutt_dato": slutt_dato}
        ).fetchone()[0]
    finally:
        con.close()


def svarteliste(epost: str):
    try:
        prikker = antall_prikker_siste_maaned(epost)

        if prikker < 3:
            print(f"Bruker {epost} har ikke tre prikker siste 30 dager.")
            sys.exit(1)

        print(f"Bruker {epost} er svartelistet.")
    except ValueError as e:
        print(e)
        sys.exit(1)
    except sqlite3.Error as e:
        print(f"Feil: {e}")
        sys.exit(1)


