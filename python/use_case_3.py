"""
Registrering av oppmøte for treningen nevnt i brukstilfelle 2. Brukernavn og
hvilken trening skal være parametere. Denne skal leveres som Python og SQL.
"""


"""
Vi bruker epost som brukernavn.
"""

import sqlite3
import sys
from db import get_connection

# Parametere
EPOST = "johnny@stud.ntnu.no"
TRENING_ID = 1
PROFIL_ID = 1

def registrer_oppmote(epost: str, trening_id: int):
    con = get_connection()

    try:
        # Steg 1: Finn profil
        profil = con.execute(
            "SELECT ID, fornavn, etternavn FROM Profil WHERE epost = :epost",
            {"epost": epost}
        ).fetchone()

        if profil is None:
            print(f"Feil: Fant ingen bruker med epost '{epost}'.")
            sys.exit(1)

        profil_id = profil["ID"]
        print(f"Bruker funnet: {profil['fornavn']} {profil['etternavn']} (ID {profil_id})")

        # Steg 2: Finn trening
        trening = con.execute(
            "SELECT ID FROM Gruppeaktivitet WHERE ID = :trening_id",
            {"trening_id": trening_id}
        ).fetchone()

        if trening is None:
            print(f"Feil: Fant ingen trening med ID '{trening_id}'.")
            sys.exit(1)
        
        trening_id = trening["ID"]
        print(f"Trening funnet: {trening['ID']}")

        # Steg 3: Sett inn oppmøte
        con.execute(
            "INSERT INTO møter_til_gruppe (senter_ID, sal_ID, gruppeaktivitet_ID, profil_ID) VALUES (:senter_id, :sal_id, :gruppeaktivitet_id, :profil_id)",
            {"senter_id": senter_id, "sal_id": sal_id, "gruppeaktivitet_id": gruppeaktivitet_id, "profil_id": profil_id}
        )
        con.commit()

        print(f"Oppmøte registret for {profil['fornavn']} {profil['etternavn']} (ID {profil_id})")

    except sqlite3.Error as e:
        print(f"Feil: {e}")
        con.rollback()
        sys.exit(1)
    finally:
        con.close()
