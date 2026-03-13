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

        # Steg 3: Sjekk om bruker er påmeldt til treningen og hent nødvendige nøkler
        påmeldt = con.execute(
            """
            SELECT senter_ID, sal_ID, gruppeaktivitet_ID
            FROM påmeldt_til
            WHERE profil_ID = :profil_id AND gruppeaktivitet_ID = :trening_id
            """,
            {"profil_id": profil_id, "trening_id": trening_id}
        ).fetchone()

        if påmeldt is None:
            print(f"Feil: Bruker er ikke påmeldt til treningen.")
            sys.exit(1)

        senter_id          = påmeldt["senter_ID"]
        sal_id             = påmeldt["sal_ID"]
        gruppeaktivitet_id = påmeldt["gruppeaktivitet_ID"]
        print(f"Bruker er påmeldt til trening ID {trening_id}")

        # Steg 4: Sett inn oppmøte med tidspunkt nå
        con.execute(
            """
            INSERT INTO møter_til_gruppe
                (senter_ID, sal_ID, gruppeaktivitet_ID, profil_ID, tidspunkt)
            VALUES (:senter_id, :sal_id, :gruppeaktivitet_id, :profil_id,
                    datetime('now', 'localtime'))
            """,
            {"senter_id": senter_id, "sal_id": sal_id,
             "gruppeaktivitet_id": gruppeaktivitet_id, "profil_id": profil_id}
        )
        con.commit()

        print(f"Oppmøte registret for {profil['fornavn']} {profil['etternavn']} (ID {profil_id})")

    except sqlite3.IntegrityError as e:
        feil = str(e)
        if "UNIQUE" in feil or "PRIMARY" in feil:
            print("Feil: Oppmøte er allerede registrert for denne treningen.")
        else:
            print(f"Feil: {e}")
        con.rollback()
        sys.exit(1)
    except sqlite3.Error as e:
        print(f"Feil: {e}")
        con.rollback()
        sys.exit(1)
    
    finally:
        con.close()
