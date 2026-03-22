"""
4. Ukeplan for alle treninger registrert i uke 12, dvs. fra 16.mars til 23.mars. Denne
skal sorteres på tid, dvs. treninger fra forskjellige senter skal flettes inn i samme
output. Dette skal leveres i Pyhton og SQL. Startdag og uke skal være parametere
som settes før du kjører queriet.
"""

import datetime
import sqlite3
import sys
from db import get_connection

# Parametere
START_DAG = "2026-03-16"
UKE = 12


def ukeplan(start_dag: str, uke: int):
    # Oppgaven krever både startdag og uke som parametere, men de er redundante:
    # kjenner man startdagen vet man uken, og omvendt. Vi bruker derfor kun
    # start_dag til å beregne datointervallet, mens uke kun vises i utskriften.
    con = get_connection()

    try:
        slutt_dag = (datetime.datetime.strptime(start_dag, "%Y-%m-%d") + datetime.timedelta(days=7)).strftime("%Y-%m-%d")

        treninger = con.execute(
            """
            SELECT
                ga.ID,
                ga.dato,
                ga.start,
                ga.slutt,
                ga.senter_ID,
                ga.sal_ID,
                ga.aktivitet_navn,
                s.navn AS senter_navn
            FROM Gruppeaktivitet ga
            JOIN Senter s ON s.ID = ga.senter_ID
            WHERE ga.dato BETWEEN :start_dag AND :slutt_dag
            ORDER BY ga.dato ASC, ga.start ASC
            """,
            {
                "start_dag": start_dag,
                "slutt_dag": slutt_dag
            }
        ).fetchall()
        print(f"Ukeplan for uke {uke} fra {start_dag} til {slutt_dag}:")
        for trening in treninger:
            print(
                f"{trening['dato']} | {trening['aktivitet_navn']} | "
                f"{trening['start']}-{trening['slutt']} | "
                f"{trening['senter_navn']} | sal {trening['sal_ID']}"
            )
    except sqlite3.Error as e:
        print(f"Feil: {e}")
        con.rollback()
        sys.exit(1)
    finally:
        con.close()
