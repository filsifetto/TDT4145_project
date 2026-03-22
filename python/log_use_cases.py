"""
log_use_cases.py – Kjører alle brukstilfeller og lagrer terminaloutput til fil.

Oppretter en fersk testdatabase, kjører migrasjonene og demonstrerer
hvert brukstilfelle med forhåndsdefinerte parametere. Resultatet skrives
til output/use_case_output.txt.

Kjør fra prosjektmappen:
    python python/log_use_cases.py
"""

import sys
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "python"))

OUTPUT_FILE = ROOT / "output" / "use_case_output.txt"


def _capture(func, *args, **kwargs) -> str:
    buf = StringIO()
    old_stdout = sys.stdout
    sys.stdout = buf
    try:
        func(*args, **kwargs)
    except SystemExit:
        pass
    except Exception as exc:
        print(f"[Feil: {exc}]")
    finally:
        sys.stdout = old_stdout
    return buf.getvalue().rstrip()


def _header(title: str) -> str:
    line = "=" * 60
    return f"\n{line}\n{title}\n{line}"


def run_all(db_path: Path) -> str:
    import db
    import db_init
    from use_case_2 import book_trening
    from use_case_3 import registrer_oppmote
    from use_case_4 import ukeplan
    from use_case_5 import personlig_besokshistorie
    from use_case_6 import svarteliste
    from use_case_7 import mest_aktive_bruker
    from use_case_8 import finn_treningspartnere

    sections = []

    # Simuler oppstart av main.py: skjema opprettes stille før menyen vises.
    db_init.ensure_schema()

    # ── Innlasting av data (menyvalg 1) ──────────────────────────────────────
    sections.append(_header("INNLASTING AV DATA (menyvalg 1 – kjør migrasjoner)"))
    sections.append(_capture(db_init.run_migrations, verbose=True))

    # ── BT2: Book trening ────────────────────────────────────────────────────
    sections.append(_header("BRUKSTILFELLE 2: Book trening"))
    sections.append("Scenario A – booking som allerede er registrert i demo-data:")
    sections.append(
        _capture(
            book_trening,
            "johnny@stud.ntnu.no", "Spin60", "2026-03-17", "18:30",
            "Øya treningssenter",
        )
    )
    sections.append("\nScenario B – ny booking (HIIT, Moholt, 20. mars):")
    sections.append(
        _capture(
            book_trening,
            "johnny@stud.ntnu.no", "HIIT", "2026-03-20", "07:00",
            "Moholt",
        )
    )
    sections.append("\nScenario C – forsøk med svartelistet bruker (Mikkel, 3 prikker):")
    sections.append(
        _capture(
            book_trening,
            "mikkels@stud.ntnu.no", "Spin60", "2026-03-17", "18:30",
            "Øya treningssenter",
        )
    )

    # ── BT3: Registrer oppmøte ───────────────────────────────────────────────
    sections.append(_header("BRUKSTILFELLE 3: Registrer oppmøte"))
    sections.append(
        "Forsøk på å registrere oppmøte for en aktivitet som allerede er over\n"
        "(demonstrerer at triggeren 'check_møter_til_gruppe_etter_slutt' virker):"
    )
    sections.append(
        _capture(registrer_oppmote, "johnny@stud.ntnu.no", 7)
    )

    # ── BT4: Ukeplan ─────────────────────────────────────────────────────────
    sections.append(_header("BRUKSTILFELLE 4: Ukeplan (uke 12, start 2026-03-16)"))
    sections.append(_capture(ukeplan, "2026-03-16", 12))

    # ── BT5: Personlig besøkshistorie ─────────────────────────────────────────
    sections.append(_header("BRUKSTILFELLE 5: Personlig besøkshistorie"))
    sections.append("johnny@stud.ntnu.no siden 2026-01-01:")
    sections.append(
        _capture(personlig_besokshistorie, "johnny@stud.ntnu.no", "2026-01-01")
    )

    # ── BT6: Svartelisting ───────────────────────────────────────────────────
    sections.append(_header("BRUKSTILFELLE 6: Svartelisting"))
    sections.append("mikkels@stud.ntnu.no (3 prikker siste 30 dager → svartelistet):")
    sections.append(_capture(svarteliste, "mikkels@stud.ntnu.no"))
    sections.append("\njohnny@stud.ntnu.no (ingen prikker → ikke svartelistet):")
    sections.append(_capture(svarteliste, "johnny@stud.ntnu.no"))

    # ── BT7: Mest aktive bruker ──────────────────────────────────────────────
    sections.append(_header("BRUKSTILFELLE 7: Mest aktive bruker (mars 2026)"))
    sections.append(_capture(mest_aktive_bruker, 3))

    # ── BT8: Finn treningspartnere ───────────────────────────────────────────
    sections.append(_header("BRUKSTILFELLE 8: Finn treningspartnere"))
    sections.append(_capture(finn_treningspartnere))

    sections.append("\n" + "=" * 60)
    return "\n".join(sections)


def main() -> None:
    OUTPUT_FILE.parent.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "treningdb.sqlite"
        with patch("db.DB_PATH", db_path):
            output = run_all(db_path)

    OUTPUT_FILE.write_text(output, encoding="utf-8")
    print(f"Output skrevet til {OUTPUT_FILE}")
    print()
    print(output)


if __name__ == "__main__":
    main()
