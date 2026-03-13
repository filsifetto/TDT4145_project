from use_case_6 import antall_prikker_siste_maaned
"""
Brukstilfelle 2 - Booking av gruppetime

Booker en navngitt gruppeaktivitet på et gitt tidspunkt og senter
for en bruker identifisert med epost.

Kjør:
    python python/use_case_2.py
"""

import sqlite3
import sys
from db import get_connection

# Parametere
EPOST       = "johnny@stud.ntnu.no"
AKTIVITET   = "Spin60"
DATO        = "2026-03-17"
STARTTID    = "18:30"
SENTER_NAVN = "Øya treningssenter"


def book_trening(epost: str, aktivitet: str, dato: str,
                 starttid: str, senter_navn: str) -> None:

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

        prikker = antall_prikker_siste_maaned(epost)
        if prikker >= 3:
            print(f"Bruker {profil['fornavn']} {profil['etternavn']} er svartelistet.")
            sys.exit(1)

        

        # Steg 2: Finn gruppeaktiviteten
        aktivitet_rad = con.execute(
            """
            SELECT ga.senter_ID, ga.sal_ID, ga.ID AS ga_id,
                   ga.start, ga.slutt, s.navn AS senter
            FROM Gruppeaktivitet ga
            JOIN Senter s ON s.ID = ga.senter_ID
            WHERE ga.aktivitet_navn = :aktivitet
              AND ga.dato           = :dato
              AND ga.start          = :starttid
              AND s.navn            = :senter_navn
            """,
            {"aktivitet": aktivitet, "dato": dato,
             "starttid": starttid, "senter_navn": senter_navn}
        ).fetchone()

        if aktivitet_rad is None:
            print(
                f"Feil: Fant ingen trening '{aktivitet}' "
                f"den {dato} kl. {starttid} på {senter_navn}."
            )
            sys.exit(1)

        senter_id = aktivitet_rad["senter_ID"]
        sal_id    = aktivitet_rad["sal_ID"]
        ga_id     = aktivitet_rad["ga_id"]

        print(
            f"Trening funnet: {aktivitet} - {dato} kl. {aktivitet_rad['start']}-"
            f"{aktivitet_rad['slutt']} på {aktivitet_rad['senter']}"
        )

        # Steg 3: Sett inn booking
        # påmelding_nummer = neste ledige nummer (ventelisterekkefølge)
        con.execute(
            """
            INSERT INTO påmeldt_til
                (senter_ID, sal_ID, gruppeaktivitet_ID, profil_ID, påmelding_nummer)
            VALUES (:senter_id, :sal_id, :ga_id, :profil_id,
                COALESCE(
                    (SELECT MAX(påmelding_nummer)
                     FROM påmeldt_til
                     WHERE senter_ID          = :senter_id
                       AND sal_ID             = :sal_id
                       AND gruppeaktivitet_ID = :ga_id),
                    0) + 1
            )
            """,
            {"senter_id": senter_id, "sal_id": sal_id,
             "ga_id": ga_id, "profil_id": profil_id}
        )
        con.commit()

        # Steg 4: Bekreftelse
        rang = con.execute(
            """
            SELECT påmelding_nummer FROM påmeldt_til
            WHERE senter_ID          = :senter_id
              AND sal_ID             = :sal_id
              AND gruppeaktivitet_ID = :ga_id
              AND profil_ID          = :profil_id
            """,
            {"senter_id": senter_id, "sal_id": sal_id,
             "ga_id": ga_id, "profil_id": profil_id}
        ).fetchone()["påmelding_nummer"]

        kapasitet = con.execute(
            "SELECT kapasitet FROM Sal WHERE senter_ID = :senter_id AND ID = :sal_id",
            {"senter_id": senter_id, "sal_id": sal_id}
        ).fetchone()["kapasitet"]

        print(f"\nBooking vellykket!")
        print(f"  Aktivitet : {aktivitet}")
        print(f"  Dato/tid  : {dato} kl. {starttid}")
        print(f"  Senter    : {senter_navn}")
        print(f"  Plass nr. : {rang} av {kapasitet}")
        if rang > kapasitet:
            print(f"  ** Du er på venteliste (plass {rang - kapasitet} i køen) **")

    except sqlite3.IntegrityError as e:
        feil = str(e)
        if "utestengt" in feil:
            print("Booking avvist: Brukeren er utestengt fra nettbooking (≥3 prikker siste 30 dager).")
        elif "overlapper" in feil:
            print("Booking avvist: Brukeren er allerede påmeldt en aktivitet som overlapper i tid.")
        elif "UNIQUE" in feil or "allerede påmeldt" in feil:
            print("Booking avvist: Brukeren er allerede påmeldt denne aktiviteten.")
        else:
            print(f"Booking avvist: {feil}")
        sys.exit(1)
    finally:
        con.close()


if __name__ == "__main__":
    book_trening(EPOST, AKTIVITET, DATO, STARTTID, SENTER_NAVN)
