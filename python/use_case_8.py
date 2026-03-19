"""
Brukstilfelle 8 – Finn treningspartnere

Finner par av brukere som har trent sammen (møtt til samme
gruppeaktivitet) og teller antall felles treninger.

Kjør:
    python python/use_case_8.py
"""

from db import get_connection

QUERY = """
SELECT p1.epost AS epost_1,
       p2.epost AS epost_2,
       COUNT(*)  AS antall_felles_treninger
FROM   møter_til_gruppe m1
JOIN   møter_til_gruppe m2
       ON  m1.senter_ID          = m2.senter_ID
       AND m1.sal_ID             = m2.sal_ID
       AND m1.gruppeaktivitet_ID = m2.gruppeaktivitet_ID
       AND m1.profil_ID          < m2.profil_ID
JOIN   Profil p1 ON p1.ID = m1.profil_ID
JOIN   Profil p2 ON p2.ID = m2.profil_ID
GROUP BY m1.profil_ID, m2.profil_ID
ORDER BY antall_felles_treninger DESC;
"""


def finn_treningspartnere() -> None:
    con = get_connection()
    try:
        rader = con.execute(QUERY).fetchall()

        if not rader:
            print("Ingen par av brukere har trent sammen.")
            return

        print(f"\n{'Bruker 1':<30} {'Bruker 2':<30} {'Felles treninger':>17}")
        print("-" * 79)
        for rad in rader:
            print(f"{rad['epost_1']:<30} {rad['epost_2']:<30} {rad['antall_felles_treninger']:>17}")
    finally:
        con.close()


if __name__ == "__main__":
    finn_treningspartnere()
