"""
Registrering av oppmøte for gruppetimer.

Brukeren identifiseres med epost, og funksjonen viser alle gruppetimer
brukeren er påmeldt før oppmøte registreres.
"""

import sqlite3
import sys

from db import get_connection

# Parametere
EPOST = "johnny@stud.ntnu.no"


def _skal_lukke_tilkobling(con) -> bool:
    database_path = con.execute("PRAGMA database_list").fetchone()[2]
    return bool(database_path)


def _hent_pameldte_treninger(con, profil_id: int):
    return con.execute(
        """
        SELECT
            pt.senter_ID,
            pt.sal_ID,
            pt.gruppeaktivitet_ID,
            ga.aktivitet_navn,
            ga.dato,
            ga.start,
            ga.slutt,
            s.navn AS senter_navn,
            mtg.profil_ID AS har_oppmote
        FROM påmeldt_til pt
        JOIN Gruppeaktivitet ga
          ON ga.senter_ID = pt.senter_ID
         AND ga.sal_ID = pt.sal_ID
         AND ga.ID = pt.gruppeaktivitet_ID
        JOIN Senter s
          ON s.ID = ga.senter_ID
        LEFT JOIN møter_til_gruppe mtg
          ON mtg.senter_ID = pt.senter_ID
         AND mtg.sal_ID = pt.sal_ID
         AND mtg.gruppeaktivitet_ID = pt.gruppeaktivitet_ID
         AND mtg.profil_ID = pt.profil_ID
        WHERE pt.profil_ID = ?
        ORDER BY ga.dato, ga.start, ga.aktivitet_navn, s.navn
        """,
        (profil_id,),
    ).fetchall()


def _skriv_pameldte_treninger(treninger):
    print("\nPåmeldte treninger:")
    for index, trening in enumerate(treninger, start=1):
        status = "oppmøte registrert" if trening["har_oppmote"] is not None else "ikke registrert"
        print(
            f"{index}. {trening['aktivitet_navn']} | {trening['dato']} | "
            f"{trening['start']}-{trening['slutt']} | {trening['senter_navn']} | {status}"
        )


def _velg_trening(treninger, trening_valg):
    if isinstance(trening_valg, int) or (
        isinstance(trening_valg, str) and trening_valg.strip().isdigit()
    ):
        valgt_id = int(trening_valg)
        for trening in treninger:
            if trening["gruppeaktivitet_ID"] == valgt_id:
                return trening
        return None

    if trening_valg is None:
        trening_valg = input("Skriv navnet på treningen du vil registrere oppmøte for: ").strip()
    else:
        trening_valg = str(trening_valg).strip()

    if not trening_valg:
        return None

    eksakte = [
        trening for trening in treninger
        if trening["aktivitet_navn"].lower() == trening_valg.lower()
    ]
    if len(eksakte) == 1:
        return eksakte[0]
    if len(eksakte) > 1:
        print("Fant flere påmeldte treninger med samme navn. Velg nummeret fra listen.")
        valg = input("Nummer: ").strip()
        if valg.isdigit():
            indeks = int(valg)
            if 1 <= indeks <= len(treninger):
                return treninger[indeks - 1]
        return None

    delvise = [
        trening for trening in treninger
        if trening_valg.lower() in trening["aktivitet_navn"].lower()
    ]
    if len(delsvise) == 1:
        return delvise[0]
    if len(delsvise) > 1:
        print("Fant flere treff. Velg nummeret fra listen.")
        valg = input("Nummer: ").strip()
        if valg.isdigit():
            indeks = int(valg)
            if 1 <= indeks <= len(treninger):
                return treninger[indeks - 1]
    return None


def registrer_oppmote(epost: str, trening_valg=None):
    con = get_connection()
    skal_lukkes = _skal_lukke_tilkobling(con)

    try:
        profil = con.execute(
            "SELECT ID, fornavn, etternavn FROM Profil WHERE epost = ?",
            (epost,),
        ).fetchone()

        if profil is None:
            print(f"Feil: Fant ingen bruker med epost '{epost}'.")
            sys.exit(1)

        profil_id = profil["ID"]
        print(f"Bruker funnet: {profil['fornavn']} {profil['etternavn']} (ID {profil_id})")

        treninger = _hent_pameldte_treninger(con, profil_id)
        if not treninger:
            print("Feil: Bruker er ikke påmeldt noen gruppetimer.")
            sys.exit(1)

        _skriv_pameldte_treninger(treninger)
        trening = _velg_trening(treninger, trening_valg)

        if trening is None:
            print(f"Feil: Fant ingen påmeldt trening som matcher '{trening_valg}'.")
            sys.exit(1)

        print(
            f"Valgt trening: {trening['aktivitet_navn']} - {trening['dato']} "
            f"kl. {trening['start']} på {trening['senter_navn']}"
        )

        con.execute(
            """
            INSERT INTO møter_til_gruppe
                (senter_ID, sal_ID, gruppeaktivitet_ID, profil_ID, tidspunkt)
            VALUES (?, ?, ?, ?, datetime('now', 'localtime'))
            """,
            (
                trening["senter_ID"],
                trening["sal_ID"],
                trening["gruppeaktivitet_ID"],
                profil_id,
            ),
        )
        con.commit()

        print(f"Oppmøte registrert for {profil['fornavn']} {profil['etternavn']} (ID {profil_id})")

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
        if skal_lukkes:
            con.close()


if __name__ == "__main__":
    registrer_oppmote(EPOST)
