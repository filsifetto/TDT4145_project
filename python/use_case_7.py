"""
7. Hver måned blir personen/personene som har trent flest fellestreninger, gitt
oppmerksomhet. Lag et query som finner den/de som har deltatt på flest
gruppetimer en gitt måned. Det kan være flere enn en person. Denne kan lages i
Python og SQL. Husk å ta med måned som parameter. Legg inn noen som har
trent slik at du viser at queriet virker.
"""

import calendar
import sqlite3
import sys
from datetime import datetime, timedelta
from db import get_connection

# Parametere
MAANED = 3

def mest_aktive_bruker(maaned: int):
    con = get_connection()

    try:
        aar = datetime.now().year
        start_dato = datetime(aar, maaned, 1)
        siste_dag = calendar.monthrange(aar, maaned)[1]
        slutt_dato = datetime(aar, maaned, siste_dag)
        start_str = start_dato.strftime("%Y-%m-%d")
        slutt_str = slutt_dato.strftime("%Y-%m-%d")

        # Finn profil_ID, fornavn, etternavn og antall for de som har flest gruppetimer (kan være flere)
        brukere = con.execute(
            """
            WITH counts AS (
                SELECT profil_ID, COUNT(*) as cnt
                FROM møter_til_gruppe
                WHERE date(tidspunkt) BETWEEN :start_dato AND :slutt_dato
                GROUP BY profil_ID
            ),
            maks AS (SELECT MAX(cnt) as m FROM counts)
            SELECT c.profil_ID, c.cnt, p.fornavn, p.etternavn
            FROM counts c
            JOIN maks m ON c.cnt = m.m
            JOIN Profil p ON c.profil_ID = p.ID
            """,
            {"start_dato": start_str, "slutt_dato": slutt_str}
        ).fetchall()

        print(f"Personen/personene som har deltatt på flest gruppetimer i måned {maaned}:")
        if not brukere:
            print("Ingen treninger registrert i denne måneden.")
        else:
            for b in brukere:
                print(f" {b['fornavn']} {b['etternavn']} har deltatt på flest gruppetimer")
    
    except sqlite3.Error as e:
        print(f"Feil: {e}")
        con.rollback()
        sys.exit(1)
    finally:
        con.close()