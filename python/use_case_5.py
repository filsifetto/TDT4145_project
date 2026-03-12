"""
5. Lag en personlig besøkshistorie for bruker «johnny@stud.ntnu.no» siden 1. januar
2026. Denne kan lages i SQL. Sørg for at det er registrert noen treninger for Johnny
i databasen. Skriv ut hvilken trening, treningssenter og dato/tid for treningen.
Resultatet skal inneholde unike rader.
"""

import sqlite3
import sys
from datetime import datetime
from db import get_connection

# Parametere
EPOST = "johnny@stud.ntnu.no"
START_DATO = "2026-01-01"


def personlig_besokshistorie(epost: str, start_dato: str):
    con = get_connection()

    try:
        profil_id = con.execute(
            "SELECT ID FROM Profil WHERE epost = :epost",
            {"epost": epost}
        ).fetchone()["ID"]

        # Steg 1: Finn treninger bruker har møtt til (via møter_til_gruppe)
        treninger_query = """
            SELECT ga.ID, ga.start, ga.slutt, ga.senter_ID, ga.sal_ID, ga.aktivitet_navn, ga.dato
            FROM møter_til_gruppe mtg
            JOIN Gruppeaktivitet ga ON ga.senter_ID = mtg.senter_ID AND ga.sal_ID = mtg.sal_ID AND ga.ID = mtg.gruppeaktivitet_ID
            WHERE mtg.profil_ID = :profil_id AND ga.dato BETWEEN :start_dato AND :slutt_dato
            ORDER BY ga.dato ASC, ga.start ASC
        """
        params = {"profil_id": profil_id, "start_dato": start_dato, "slutt_dato": datetime.now().strftime("%Y-%m-%d")}
        treninger = con.execute(treninger_query, params).fetchall()

        print(f"Personlig besøkshistorie for {epost} siden {start_dato}:")
        for trening in treninger:
            print(f"Trening {trening['aktivitet_navn']} fra {trening['start']} til {trening['slutt']} på senter {trening['senter_ID']} sal {trening['sal_ID']} ({trening['dato']})")
    except sqlite3.Error as e:
        print(f"Feil: {e}")
        con.rollback()
        sys.exit(1)
    finally:
        con.close()