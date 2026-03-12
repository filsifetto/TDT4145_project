import datetime
"""
4. Ukeplan for alle treninger registrert i uke 12, dvs. fra 16.mars til 23.mars. Denne
skal sorteres på tid, dvs. treninger fra forskjellige senter skal flettes inn i samme
output. Dette skal leveres i Pyhton og SQL. Startdag og uke skal være parametere
som settes før du kjører queriet.
"""


"""
Hvorfor er både startdag og uke parametere?
"""

import sqlite3
import sys
from db import get_connection

# Parametere
START_DAG = "2026-03-16"
UKE = 12

"""
Printer en oversikt over alle treninger registrert i uke 12, dvs. fra 16.mars til 23.mars.
"""


def ukeplan(start_dag: str, uke: int):
    con = get_connection()

    try:
        # Steg 1: Finn treninger sortert på tid
        treninger = con.execute(
            "SELECT ID, start, slutt, senter_ID, sal_ID, aktivitet_navn FROM Gruppeaktivitet WHERE dato BETWEEN :start_dag AND :slutt_dag ORDER BY dato ASC, start ASC",
            {
                "start_dag": start_dag,
                "slutt_dag": (datetime.datetime.strptime(start_dag, "%Y-%m-%d") + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
            }
        ).fetchall()
        slutt_dag = (datetime.datetime.strptime(start_dag, "%Y-%m-%d") + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        print(f"Ukeplan for uke {uke} fra {start_dag} til {slutt_dag}:")
        for trening in treninger:
            print(f"Trening {trening['aktivitet_navn']} fra {trening['start']} til {trening['slutt']} på senter {trening['senter_ID']} sal {trening['sal_ID']}")
    except sqlite3.Error as e:
        print(f"Feil: {e}")
        con.rollback()
        sys.exit(1)
    finally:
        con.close()