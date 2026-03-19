"""
tests.py – Tester for SQL-skjema (triggere/constraints) og brukstilfeller 2 og 3.

Kjør:
    cd /path/to/TDT4145_project
    python -m unittest python/tests.py -v
  eller:
    python -m pytest python/tests.py -v
"""

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from io import StringIO

# ─── Hjelpefunksjoner ───────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "python"))
SCHEMA_PATH = ROOT / "sql" / "create_tables.sql"
INSERTS_PATH = ROOT / "sql" / "insert_data.sql"


def build_db() -> sqlite3.Connection:
    """Oppretter en tom in-memory-database med skjemaet fra create_tables.sql."""
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA_PATH.read_text())
    return con


def build_db_with_data() -> sqlite3.Connection:
    """Oppretter en in-memory-database med skjema OG testdata."""
    con = build_db()
    con.executescript(INSERTS_PATH.read_text())
    return con


def _table_count(con: sqlite3.Connection, table_name: str) -> int:
    return con.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[0]


def _insert_base_fixtures(con: sqlite3.Connection):
    """Setter inn minimalt sett med felles testdata (senter, sal, profiler, aktivitet)."""
    con.executescript("""
        INSERT INTO Senter (ID, navn, gate, nummer, fra, til)
            VALUES (1, 'TestSenter', 'Testgate', '1', '06:00', '22:00');

        INSERT INTO Sal (senter_ID, ID, type, kapasitet)
            VALUES (1, 1, 'spinning', 2);

        INSERT INTO Aktivitet (navn, kategori) VALUES ('Spin60', 'Spin');

        INSERT INTO Profil (ID, type, fornavn, etternavn, epost, telefon)
            VALUES (1, 'ansatt', 'Hanne', 'Fjeld', 'hanne@test.no', '90000001');

        INSERT INTO Profil (ID, type, fornavn, etternavn, epost, telefon)
            VALUES (2, 'medlem', 'Johnny', 'Olsen', 'johnny@test.no', '90000002');

        INSERT INTO Profil (ID, type, fornavn, etternavn, epost, telefon)
            VALUES (3, 'medlem', 'Emma', 'Bakke', 'emma@test.no', '90000003');
    """)


class TestDataImport(unittest.TestCase):
    """Tester brukstilfelle 1 og additiv innlasting av demo-data."""

    def test_build_demo_source_reconciles_conflicting_bookings(self):
        """Kildedatasettet skal beholde flere deltakere per time, men hoppe over dubletter."""
        import data_sync

        con = data_sync.build_demo_source()
        self.addCleanup(con.close)

        ga7 = con.execute(
            """
            SELECT profil_ID, påmelding_nummer
            FROM påmeldt_til
            WHERE senter_ID = 1 AND sal_ID = 1 AND gruppeaktivitet_ID = 7
            ORDER BY påmelding_nummer
            """
        ).fetchall()
        ga1 = con.execute(
            """
            SELECT profil_ID, påmelding_nummer
            FROM påmeldt_til
            WHERE senter_ID = 1 AND sal_ID = 1 AND gruppeaktivitet_ID = 1
            ORDER BY påmelding_nummer
            """
        ).fetchall()

        self.assertEqual([(row["profil_ID"], row["påmelding_nummer"]) for row in ga7],
                         [(4, 1), (5, 2), (6, 3), (7, 4), (8, 5)])
        self.assertEqual([(row["profil_ID"], row["påmelding_nummer"]) for row in ga1],
                         [(4, 1), (5, 2), (6, 3), (10, 4)])

    def test_sync_demo_data_only_adds_missing_rows(self):
        """Brukstilfelle 1 skal ikke bygge databasen på nytt eller slette eksisterende data."""
        import db
        import data_sync

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_db = Path(tmpdir) / "treningdb.sqlite"
            with patch("db.DB_PATH", temp_db):
                con = db.get_connection()
                con.executescript(SCHEMA_PATH.read_text())
                con.executescript(INSERTS_PATH.read_text())
                con.execute(
                    """
                    INSERT INTO Profil (ID, type, fornavn, etternavn, epost, telefon)
                    VALUES (99, 'medlem', 'Behold', 'Meg', 'behold.meg@test.no', '99999999')
                    """
                )
                con.commit()
                before_profiles = _table_count(con, "Profil")
                con.close()

                data_sync.sync_demo_data()

                repaired = db.get_connection()
                self.addCleanup(repaired.close)

                self.assertEqual(
                    repaired.execute("SELECT COUNT(*) FROM Profil WHERE ID = 99").fetchone()[0],
                    1,
                )
                self.assertGreater(_table_count(repaired, "Profil"), before_profiles)
                self.assertEqual(
                    repaired.execute(
                        """
                        SELECT påmelding_nummer
                        FROM påmeldt_til
                        WHERE senter_ID = 1 AND sal_ID = 1 AND gruppeaktivitet_ID = 7 AND profil_ID = 8
                        """
                    ).fetchone()[0],
                    5,
                )
                self.assertEqual(
                    repaired.execute(
                        """
                        SELECT påmelding_nummer
                        FROM påmeldt_til
                        WHERE senter_ID = 1 AND sal_ID = 1 AND gruppeaktivitet_ID = 1 AND profil_ID = 10
                        """
                    ).fetchone()[0],
                    4,
                )

    def test_get_connection_migrates_old_påmeldt_til_schema(self):
        """Eksisterende databasefiler med gammel påmeldt_til-struktur skal oppgraderes automatisk."""
        import db

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_db = Path(tmpdir) / "treningdb.sqlite"
            con = sqlite3.connect(temp_db)
            con.executescript(SCHEMA_PATH.read_text())
            con.executescript("""
                DROP TRIGGER IF EXISTS sett_påmelding_nummer_insert;
                DROP TRIGGER IF EXISTS check_avbestillingsfrist;
                DROP TRIGGER IF EXISTS check_bruker_overlapp_påmeldt_insert;
                DROP TRIGGER IF EXISTS check_bruker_overlapp_påmeldt_update;
                DROP TRIGGER IF EXISTS check_utestengelse_insert;
                DROP TRIGGER IF EXISTS check_utestengelse_update;
                DROP TABLE påmeldt_til;
                CREATE TABLE påmeldt_til (
                    senter_ID          INTEGER NOT NULL,
                    sal_ID             INTEGER NOT NULL,
                    gruppeaktivitet_ID INTEGER NOT NULL,
                    profil_ID          INTEGER NOT NULL,
                    påmelding_nummer   INTEGER NOT NULL,
                    PRIMARY KEY (senter_ID, sal_ID, gruppeaktivitet_ID, profil_ID),
                    UNIQUE (senter_ID, sal_ID, gruppeaktivitet_ID, påmelding_nummer),
                    FOREIGN KEY (senter_ID, sal_ID, gruppeaktivitet_ID)
                        REFERENCES Gruppeaktivitet(senter_ID, sal_ID, ID) ON DELETE CASCADE,
                    FOREIGN KEY (profil_ID) REFERENCES Profil(ID) ON DELETE CASCADE
                );
            """)
            con.commit()
            con.close()

            with patch("db.DB_PATH", temp_db):
                migrated = db.get_connection()
                self.addCleanup(migrated.close)

                info = migrated.execute("PRAGMA table_info('påmeldt_til')").fetchall()
                pamelding_not_null = next(row["notnull"] for row in info if row["name"] == "påmelding_nummer")
                trigger = migrated.execute(
                    "SELECT name FROM sqlite_master WHERE type='trigger' AND name='sett_påmelding_nummer_insert'"
                ).fetchone()
                lingering_refs = migrated.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE sql LIKE '%påmeldt_til_gammel%'"
                ).fetchone()[0]

                self.assertEqual(pamelding_not_null, 0)
                self.assertIsNotNone(trigger)
                self.assertEqual(lingering_refs, 0)


class TestMainMenu(unittest.TestCase):
    """Tester at menyloopen tåler forventede feil i brukstilfellene."""

    def test_kjor_menyalternativ_svelger_systemexit(self):
        import main

        called = {"ran": False}

        def _action():
            called["ran"] = True
            raise SystemExit(1)

        main._kjor_menyalternativ(_action)
        self.assertTrue(called["ran"])


# ─── TestSchema ─────────────────────────────────────────────────────────────

class TestSchema(unittest.TestCase):
    """Tester at SQL-skjemaet og alle triggere fungerer korrekt."""

    def setUp(self):
        self.con = build_db()
        _insert_base_fixtures(self.con)

    def tearDown(self):
        self.con.close()

    def _insert_ga(self, senter_id=1, sal_id=1, ga_id=1,
                   start="10:00", slutt="11:00", dato="2030-01-01",
                   aktivitet="Spin60", instrukt_id=1):
        self.con.execute(
            """INSERT INTO Gruppeaktivitet
               (senter_ID, sal_ID, ID, start, slutt, dato, aktivitet_navn, instrukt_ID)
               VALUES (?,?,?,?,?,?,?,?)""",
            (senter_id, sal_id, ga_id, start, slutt, dato, aktivitet, instrukt_id)
        )
        self.con.commit()

    # -- Tabeller oppretter korrekt ------------------------------------------

    def test_tabeller_opprettet(self):
        tabeller = {row[0] for row in self.con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        forventet = {
            "Fasilitet", "Senter", "Idrettslag", "Profil", "Aktivitet",
            "har_fasilitet", "Bemanning", "Sal", "Tredemølle", "Sykkel",
            "Gruppe", "Prikk", "er_medlem", "Idrettslagstime",
            "møter_til_idrett", "Gruppeaktivitet", "møter_til_gruppe",
            "påmeldt_til",
        }
        self.assertTrue(forventet.issubset(tabeller))

    # -- Instruktørrolle -------------------------------------------------------

    def test_check_instruktør_rolle_avvist(self):
        """Et medlem (type='medlem') skal ikke kunne settes som instruktør."""
        with self.assertRaises(sqlite3.OperationalError) as ctx:
            self._insert_ga(instrukt_id=2)  # profil 2 er 'medlem'
        self.assertIn("ansatt", str(ctx.exception))

    def test_check_instruktør_rolle_godkjent(self):
        """En ansatt skal kunne settes som instruktør uten feil."""
        self._insert_ga(instrukt_id=1)  # profil 1 er 'ansatt'
        count = self.con.execute("SELECT COUNT(*) FROM Gruppeaktivitet").fetchone()[0]
        self.assertEqual(count, 1)

    # -- Instruktøroverlapp ----------------------------------------------------

    def test_check_instruktør_overlapp_avvist(self):
        """Samme instruktør kan ikke lede to aktiviteter som overlapper."""
        self._insert_ga(ga_id=1, start="10:00", slutt="11:00")
        with self.assertRaises(sqlite3.OperationalError) as ctx:
            self._insert_ga(ga_id=2, sal_id=1, start="10:30", slutt="11:30")
        self.assertIn("overlapper", str(ctx.exception))

    def test_check_instruktør_overlapp_godkjent(self):
        """To ikke-overlappende aktiviteter med samme instruktør er ok."""
        self._insert_ga(ga_id=1, start="10:00", slutt="11:00")
        self._insert_ga(ga_id=2, start="11:00", slutt="12:00")
        count = self.con.execute("SELECT COUNT(*) FROM Gruppeaktivitet").fetchone()[0]
        self.assertEqual(count, 2)

    # -- Sal-booking overlapp (gruppe) -----------------------------------------

    def test_check_sal_booking_overlapp_gruppe_avvist(self):
        """En sal kan ikke bookes av to gruppeaktiviteter i overlappende tid."""
        self.con.execute(
            "INSERT INTO Profil (ID, type, fornavn, etternavn, epost, telefon) "
            "VALUES (4, 'ansatt', 'Torben', 'Vik', 'torben@test.no', '90000004')"
        )
        self.con.commit()
        self._insert_ga(ga_id=1, instrukt_id=1, start="10:00", slutt="11:00")
        with self.assertRaises(sqlite3.OperationalError) as ctx:
            self._insert_ga(ga_id=2, instrukt_id=4, start="10:30", slutt="11:30")
        self.assertIn("booket", str(ctx.exception))

    def test_check_sal_booking_overlapp_gruppe_godkjent(self):
        """To gruppeaktiviteter i samme sal, men ulik tid, er ok."""
        self._insert_ga(ga_id=1, start="10:00", slutt="11:00")
        self.con.execute(
            "INSERT INTO Profil (ID, type, fornavn, etternavn, epost, telefon) "
            "VALUES (4, 'ansatt', 'Torben', 'Vik', 'torben@test.no', '90000004')"
        )
        self.con.commit()
        self._insert_ga(ga_id=2, instrukt_id=4, start="11:00", slutt="12:00")
        count = self.con.execute("SELECT COUNT(*) FROM Gruppeaktivitet").fetchone()[0]
        self.assertEqual(count, 2)

    # -- Utestengelse (svartelisting) ------------------------------------------

    def test_check_utestengelse_avvist(self):
        """En bruker med 3 prikker siste 30 dager skal ikke kunne melde seg på."""
        self._insert_ga()
        self.con.executescript("""
            INSERT INTO Prikk (profil_ID, ID, dato) VALUES
                (2, 1, date('now', 'localtime', '-5 days')),
                (2, 2, date('now', 'localtime', '-10 days')),
                (2, 3, date('now', 'localtime', '-15 days'));
        """)
        with self.assertRaises(sqlite3.OperationalError) as ctx:
            self.con.execute(
                "INSERT INTO påmeldt_til VALUES (1,1,1,2,1)"
            )
        self.assertIn("utestengt", str(ctx.exception))

    def test_check_utestengelse_godkjent(self):
        """En bruker med 2 prikker siste 30 dager kan melde seg på."""
        self._insert_ga()
        self.con.executescript("""
            INSERT INTO Prikk (profil_ID, ID, dato) VALUES
                (2, 1, date('now', 'localtime', '-5 days')),
                (2, 2, date('now', 'localtime', '-10 days'));
        """)
        self.con.execute("INSERT INTO påmeldt_til VALUES (1,1,1,2,1)")
        self.con.commit()
        count = self.con.execute("SELECT COUNT(*) FROM påmeldt_til").fetchone()[0]
        self.assertEqual(count, 1)

    def test_påmelding_nummer_settes_automatisk(self):
        """Påmelding uten eksplisitt nummer skal få neste ledige påmelding_nummer."""
        self._insert_ga()
        self.con.execute(
            """
            INSERT INTO påmeldt_til
                (senter_ID, sal_ID, gruppeaktivitet_ID, profil_ID)
            VALUES (1,1,1,2)
            """
        )
        self.con.execute(
            """
            INSERT INTO påmeldt_til
                (senter_ID, sal_ID, gruppeaktivitet_ID, profil_ID)
            VALUES (1,1,1,3)
            """
        )
        self.con.commit()

        rows = self.con.execute(
            """
            SELECT profil_ID, påmelding_nummer
            FROM påmeldt_til
            ORDER BY påmelding_nummer
            """
        ).fetchall()
        self.assertEqual([(row[0], row[1]) for row in rows], [(2, 1), (3, 2)])

    # -- Brukeroverlapp ved påmelding ------------------------------------------

    def test_check_bruker_overlapp_påmeldt_avvist(self):
        """Bruker kan ikke melde seg på to gruppeaktiviteter som overlapper."""
        self.con.execute(
            "INSERT INTO Profil (ID, type, fornavn, etternavn, epost, telefon) "
            "VALUES (4, 'ansatt', 'Torben', 'Vik', 'torben@test.no', '90000004')"
        )
        self.con.execute(
            "INSERT INTO Sal (senter_ID, ID, type, kapasitet) VALUES (1, 2, 'styrke', 5)"
        )
        self.con.commit()
        self._insert_ga(sal_id=1, ga_id=1, start="10:00", slutt="11:00", instrukt_id=1)
        self.con.execute(
            "INSERT INTO Gruppeaktivitet VALUES (1,2,2,'10:30','11:30','2030-01-01','Spin60',4)"
        )
        self.con.commit()
        self.con.execute("INSERT INTO påmeldt_til VALUES (1,1,1,2,1)")
        self.con.commit()
        with self.assertRaises(sqlite3.OperationalError) as ctx:
            self.con.execute("INSERT INTO påmeldt_til VALUES (1,2,2,2,1)")
        self.assertIn("overlapper", str(ctx.exception))

    # -- Avbestillingsfrist ----------------------------------------------------

    def test_check_avbestillingsfrist_avvist(self):
        """Avbestilling innen 1 time før start skal avvises."""
        # Aktivitet starter om 30 minutter
        self.con.execute(
            """INSERT INTO Gruppeaktivitet
               (senter_ID, sal_ID, ID, start, slutt, dato, aktivitet_navn, instrukt_ID)
               VALUES (1,1,1,
                       strftime('%H:%M', datetime('now','localtime','+30 minutes')),
                       strftime('%H:%M', datetime('now','localtime','+90 minutes')),
                       date('now','localtime'),
                       'Spin60', 1)"""
        )
        self.con.execute("INSERT INTO påmeldt_til VALUES (1,1,1,2,1)")
        self.con.commit()
        with self.assertRaises(sqlite3.OperationalError) as ctx:
            self.con.execute("DELETE FROM påmeldt_til WHERE profil_ID=2")
        self.assertIn("Avbestilling", str(ctx.exception))

    def test_check_avbestillingsfrist_godkjent(self):
        """Avbestilling mer enn 1 time før start skal godkjennes."""
        self.con.execute(
            """INSERT INTO Gruppeaktivitet
               (senter_ID, sal_ID, ID, start, slutt, dato, aktivitet_navn, instrukt_ID)
               VALUES (1,1,1,
                       strftime('%H:%M', datetime('now','localtime','+3 hours')),
                       strftime('%H:%M', datetime('now','localtime','+4 hours')),
                       date('now','localtime'),
                       'Spin60', 1)"""
        )
        self.con.execute("INSERT INTO påmeldt_til VALUES (1,1,1,2,1)")
        self.con.commit()
        self.con.execute("DELETE FROM påmeldt_til WHERE profil_ID=2")
        self.con.commit()
        count = self.con.execute("SELECT COUNT(*) FROM påmeldt_til").fetchone()[0]
        self.assertEqual(count, 0)

    # -- Kapasitetsgrense gruppe -----------------------------------------------

    def test_check_kapasitet_gruppe_avvist(self):
        """Oppmøte avvises når rangens er > salens kapasitet (sal har kapasitet 2)."""
        # Sal har kapasitet 2; tre brukere melder seg på: rang 1, 2, 3
        self.con.execute(
            "INSERT INTO Profil (ID, type, fornavn, etternavn, epost, telefon) "
            "VALUES (4, 'medlem', 'Ole', 'Dahl', 'ole@test.no', '90000099')"
        )
        self.con.commit()
        self._insert_ga(start="10:00", slutt="11:00", dato="2030-06-01")
        self.con.executescript("""
            INSERT INTO påmeldt_til VALUES (1,1,1,2,1);
            INSERT INTO påmeldt_til VALUES (1,1,1,3,2);
            INSERT INTO påmeldt_til VALUES (1,1,1,4,3);
        """)
        # Brukere 2 og 3 (rang 1 og 2) kan møte opp (kapasitet=2)
        self.con.execute(
            "INSERT INTO møter_til_gruppe VALUES (1,1,1,2, datetime('now','localtime','-10 minutes'))"
        )
        self.con.execute(
            "INSERT INTO møter_til_gruppe VALUES (1,1,1,3, datetime('now','localtime','-10 minutes'))"
        )
        self.con.commit()
        # Bruker 4 (rang 3) overstiger kapasiteten
        with self.assertRaises(sqlite3.OperationalError) as ctx:
            self.con.execute(
                "INSERT INTO møter_til_gruppe VALUES (1,1,1,4, datetime('now','localtime','-10 minutes'))"
            )
        self.assertIn("kapasitetsgrensen", str(ctx.exception))

    # -- Kapasitetsgrense idrettslag -------------------------------------------

    def test_check_kapasitet_idrett_avvist(self):
        """Dropin avvises når salen er full."""
        self.con.execute(
            "INSERT INTO Idrettslag (ID, navn) VALUES (1, 'TestLag')"
        )
        self.con.execute(
            "INSERT INTO Gruppe (idrettslags_ID, ID, type) VALUES (1, 1, 'løp')"
        )
        # Sal med kapasitet 1
        self.con.execute(
            "INSERT INTO Sal (senter_ID, ID, type, kapasitet) VALUES (1, 3, 'kamp', 1)"
        )
        self.con.execute(
            "INSERT INTO Idrettslagstime "
            "(senter_ID, sal_ID, ID, type, start, slutt, dato, idrettslags_ID, gruppe_ID) "
            "VALUES (1, 3, 1, 'løp', '10:00', '11:00', '2030-06-01', 1, 1)"
        )
        self.con.executescript("""
            INSERT INTO er_medlem VALUES (1, 2);
            INSERT INTO er_medlem VALUES (1, 3);
        """)
        self.con.commit()
        # Første dropin fyller salen
        self.con.execute("INSERT INTO møter_til_idrett VALUES (1,3,1,2)")
        self.con.commit()
        # Andre dropin avvises
        with self.assertRaises(sqlite3.OperationalError) as ctx:
            self.con.execute("INSERT INTO møter_til_idrett VALUES (1,3,1,3)")
        self.assertIn("kapasitetsgrensen", str(ctx.exception))

    # -- Medlemskap ved idrettslagstime ----------------------------------------

    def test_check_medlemskap_idrett_avvist(self):
        """En ikke-medlem kan ikke møte til idrettslagstime."""
        self.con.execute(
            "INSERT INTO Idrettslag (ID, navn) VALUES (1, 'TestLag')"
        )
        self.con.execute(
            "INSERT INTO Gruppe (idrettslags_ID, ID, type) VALUES (1, 1, 'løp')"
        )
        self.con.execute(
            "INSERT INTO Sal (senter_ID, ID, type, kapasitet) VALUES (1, 3, 'kamp', 10)"
        )
        self.con.execute(
            "INSERT INTO Idrettslagstime "
            "(senter_ID, sal_ID, ID, type, start, slutt, dato, idrettslags_ID, gruppe_ID) "
            "VALUES (1, 3, 1, 'løp', '10:00', '11:00', '2030-06-01', 1, 1)"
        )
        self.con.commit()
        # profil 2 er IKKE registrert som er_medlem
        with self.assertRaises(sqlite3.OperationalError) as ctx:
            self.con.execute("INSERT INTO møter_til_idrett VALUES (1,3,1,2)")
        self.assertIn("medlem", str(ctx.exception))

    def test_check_medlemskap_idrett_godkjent(self):
        """Et registrert medlem kan møte til idrettslagstime."""
        self.con.execute(
            "INSERT INTO Idrettslag (ID, navn) VALUES (1, 'TestLag')"
        )
        self.con.execute(
            "INSERT INTO Gruppe (idrettslags_ID, ID, type) VALUES (1, 1, 'løp')"
        )
        self.con.execute(
            "INSERT INTO Sal (senter_ID, ID, type, kapasitet) VALUES (1, 3, 'kamp', 10)"
        )
        self.con.execute(
            "INSERT INTO Idrettslagstime "
            "(senter_ID, sal_ID, ID, type, start, slutt, dato, idrettslags_ID, gruppe_ID) "
            "VALUES (1, 3, 1, 'løp', '10:00', '11:00', '2030-06-01', 1, 1)"
        )
        self.con.execute("INSERT INTO er_medlem VALUES (1, 2)")
        self.con.commit()
        self.con.execute("INSERT INTO møter_til_idrett VALUES (1,3,1,2)")
        self.con.commit()
        count = self.con.execute("SELECT COUNT(*) FROM møter_til_idrett").fetchone()[0]
        self.assertEqual(count, 1)

    # -- Oppmøte etter slutt ---------------------------------------------------

    def test_check_oppmøte_etter_slutt_avvist(self):
        """Oppmøte etter aktivitetens slutt skal avvises."""
        # Aktivitet som sluttet for 10 minutter siden
        self.con.execute(
            """INSERT INTO Gruppeaktivitet
               (senter_ID, sal_ID, ID, start, slutt, dato, aktivitet_navn, instrukt_ID)
               VALUES (1,1,1,
                       strftime('%H:%M', datetime('now','localtime','-70 minutes')),
                       strftime('%H:%M', datetime('now','localtime','-10 minutes')),
                       date('now','localtime'),
                       'Spin60', 1)"""
        )
        self.con.execute("INSERT INTO påmeldt_til VALUES (1,1,1,2,1)")
        self.con.commit()
        with self.assertRaises(sqlite3.OperationalError) as ctx:
            self.con.execute(
                "INSERT INTO møter_til_gruppe VALUES (1,1,1,2, datetime('now','localtime'))"
            )
        self.assertIn("slutt", str(ctx.exception))


# ─── TestBookTrening ─────────────────────────────────────────────────────────

class TestBookTrening(unittest.TestCase):
    """Tester brukstilfelle 2 – booking av gruppetime."""

    @classmethod
    def setUpClass(cls):
        cls.full_con = build_db_with_data()

    @classmethod
    def tearDownClass(cls):
        cls.full_con.close()

    def setUp(self):
        # Rull tilbake eventuelle endringer fra forrige test
        self.full_con.execute("DELETE FROM påmeldt_til")
        self.full_con.commit()

    def _patch_con(self):
        return patch("use_case_2.get_connection", return_value=self.full_con)

    def test_vellykket_booking(self):
        """Vellykket booking oppretter en rad i påmeldt_til."""
        with self._patch_con():
            from use_case_2 import book_trening
            book_trening(
                "johnny@stud.ntnu.no", "Spin60",
                "2026-03-17", "18:30", "Øya treningssenter"
            )
        count = self.full_con.execute("SELECT COUNT(*) FROM påmeldt_til").fetchone()[0]
        self.assertEqual(count, 1)

    def test_bruker_ikke_funnet(self):
        """Ukjent epost gir SystemExit."""
        with self._patch_con():
            from use_case_2 import book_trening
            with self.assertRaises(SystemExit):
                book_trening(
                    "ukjent@test.no", "Spin60",
                    "2026-03-17", "18:30", "Øya treningssenter"
                )

    def test_aktivitet_ikke_funnet(self):
        """Feil aktivitetsnavn gir SystemExit."""
        with self._patch_con():
            from use_case_2 import book_trening
            with self.assertRaises(SystemExit):
                book_trening(
                    "johnny@stud.ntnu.no", "FinnesIkke",
                    "2026-03-17", "18:30", "Øya treningssenter"
                )

    def test_allerede_påmeldt(self):
        """Dobbel booking på samme aktivitet gir SystemExit."""
        with self._patch_con():
            from use_case_2 import book_trening
            book_trening(
                "johnny@stud.ntnu.no", "Spin60",
                "2026-03-17", "18:30", "Øya treningssenter"
            )
            with self.assertRaises(SystemExit):
                book_trening(
                    "johnny@stud.ntnu.no", "Spin60",
                    "2026-03-17", "18:30", "Øya treningssenter"
                )

    def test_utestengt_bruker(self):
        """Bruker med ≥3 prikker siste 30 dager avvises med SystemExit."""
        profil_id = self.full_con.execute(
            "SELECT ID FROM Profil WHERE epost='johnny@stud.ntnu.no'"
        ).fetchone()["ID"]
        self.full_con.executescript(f"""
            DELETE FROM Prikk WHERE profil_ID = {profil_id};
            INSERT INTO Prikk VALUES ({profil_id}, 1, date('now','localtime','-5 days'));
            INSERT INTO Prikk VALUES ({profil_id}, 2, date('now','localtime','-10 days'));
            INSERT INTO Prikk VALUES ({profil_id}, 3, date('now','localtime','-15 days'));
        """)
        try:
            with self._patch_con():
                from use_case_2 import book_trening
                with self.assertRaises(SystemExit):
                    book_trening(
                        "johnny@stud.ntnu.no", "Spin60",
                        "2026-03-17", "18:30", "Øya treningssenter"
                    )
        finally:
            self.full_con.execute(f"DELETE FROM Prikk WHERE profil_ID = {profil_id}")
            self.full_con.commit()

    def test_overlappende_booking(self):
        """Booking avvises når brukeren allerede er påmeldt en overlappende aktivitet."""
        # Spin45 starter 06:30 og slutter 07:15 – Spin60 starter 18:30 => ingen overlapp
        # Bruker melder seg først på Spin60 (18:30–19:30) og deretter på Spin45 (06:30–07:15):
        # disse overlapper ikke; istedet bruker vi to aktiviteter som faktisk overlapper.
        # Mandag 16. mars: GA ID=1 (07:00-08:00) og ID=3 (17:00-17:55) overlapper ikke.
        # Mandag 16. mars: GA ID=3 (17:00-17:55) og ID=4 (18:30-19:15) overlapper ikke.
        # Vi setter manuelt inn en overlappende aktivitet for å teste triggeren.
        # Først booke en aktivitet, deretter booke en overlappende.
        with self._patch_con():
            from use_case_2 import book_trening
            # Book Spin60 tirsdag 17. mars kl. 18:30
            book_trening(
                "johnny@stud.ntnu.no", "Spin60",
                "2026-03-17", "18:30", "Øya treningssenter"
            )
        # Manuelt sett inn en overlappende gruppeaktivitet (Spin45 kl 18:45 på en annen sal)
        self.full_con.execute(
            "INSERT INTO Sal (senter_ID, ID, type, kapasitet) VALUES (1, 10, 'yoga', 20)"
        )
        self.full_con.execute(
            "INSERT INTO Gruppeaktivitet "
            "(senter_ID, sal_ID, ID, start, slutt, dato, aktivitet_navn, instrukt_ID) "
            "VALUES (1,10,100,'18:45','19:45','2026-03-17','Spin60',12)"
        )
        self.full_con.commit()
        profil_id = self.full_con.execute(
            "SELECT ID FROM Profil WHERE epost='johnny@stud.ntnu.no'"
        ).fetchone()["ID"]
        with self.assertRaises(sqlite3.OperationalError):
            self.full_con.execute(
                "INSERT INTO påmeldt_til VALUES (1,10,100,?,1)", (profil_id,)
            )
        # Rydd opp
        self.full_con.execute("DELETE FROM Gruppeaktivitet WHERE senter_ID=1 AND sal_ID=10")
        self.full_con.execute("DELETE FROM Sal WHERE senter_ID=1 AND ID=10")
        self.full_con.commit()

    def test_venteliste(self):
        """Påmelding utover kapasiteten gir høyere påmelding_nummer enn kapasiteten."""
        kapasitet = self.full_con.execute(
            "SELECT kapasitet FROM Sal WHERE senter_ID=1 AND ID=1"
        ).fetchone()["kapasitet"]

        profiler = self.full_con.execute(
            "SELECT ID, epost FROM Profil WHERE type='medlem' LIMIT ?", (kapasitet + 1,)
        ).fetchall()

        with self._patch_con():
            from use_case_2 import book_trening
            for p in profiler:
                try:
                    book_trening(
                        p["epost"], "Spin60",
                        "2026-03-17", "18:30", "Øya treningssenter"
                    )
                except SystemExit:
                    pass  # Brukere med prikker el.l. hopper vi over

        max_nummer = self.full_con.execute(
            "SELECT MAX(påmelding_nummer) FROM påmeldt_til "
            "WHERE senter_ID=1 AND sal_ID=1 AND gruppeaktivitet_ID=7"
        ).fetchone()[0]
        self.assertIsNotNone(max_nummer)
        # Dersom mer enn kapasitet er påmeldt, finnes det venteliste-plasser
        count = self.full_con.execute(
            "SELECT COUNT(*) FROM påmeldt_til "
            "WHERE senter_ID=1 AND sal_ID=1 AND gruppeaktivitet_ID=7"
        ).fetchone()[0]
        if count > kapasitet:
            self.assertGreater(max_nummer, kapasitet)


# ─── TestRegistrerOppmote ────────────────────────────────────────────────────

class TestRegistrerOppmote(unittest.TestCase):
    """Tester brukstilfelle 3 – registrering av oppmøte."""

    def setUp(self):
        self.con = build_db()
        _insert_base_fixtures(self.con)
        # Gruppeaktivitet som er i gang akkurat nå (startet for 30 min, slutter om 30 min)
        self.con.execute(
            """INSERT INTO Gruppeaktivitet
               (senter_ID, sal_ID, ID, start, slutt, dato, aktivitet_navn, instrukt_ID)
               VALUES (1,1,1,
                       strftime('%H:%M', datetime('now','localtime','-30 minutes')),
                       strftime('%H:%M', datetime('now','localtime','+30 minutes')),
                       date('now','localtime'),
                       'Spin60', 1)"""
        )
        self.con.commit()

    def tearDown(self):
        self.con.close()

    def _patch_con(self):
        return patch("use_case_3.get_connection", return_value=self.con)

    def test_vellykket_oppmote(self):
        """Vellykket oppmøte oppretter en rad i møter_til_gruppe."""
        self.con.execute("INSERT INTO påmeldt_til VALUES (1,1,1,2,1)")
        self.con.commit()
        with self._patch_con():
            from use_case_3 import registrer_oppmote
            registrer_oppmote("johnny@test.no", 1)
        count = self.con.execute("SELECT COUNT(*) FROM møter_til_gruppe").fetchone()[0]
        self.assertEqual(count, 1)

    def test_vellykket_oppmote_med_aktivitetsnavn(self):
        """Bruker skal kunne velge trening via aktivitetsnavn i stedet for intern ID."""
        self.con.execute("INSERT INTO påmeldt_til VALUES (1,1,1,2,1)")
        self.con.commit()
        with self._patch_con(), patch("builtins.input", return_value="Spin60"):
            from use_case_3 import registrer_oppmote
            registrer_oppmote("johnny@test.no")
        count = self.con.execute("SELECT COUNT(*) FROM møter_til_gruppe").fetchone()[0]
        self.assertEqual(count, 1)

    def test_bruker_ikke_funnet(self):
        """Ukjent epost gir SystemExit."""
        with self._patch_con():
            from use_case_3 import registrer_oppmote
            with self.assertRaises(SystemExit):
                registrer_oppmote("finnesikke@test.no", 1)

    def test_trening_ikke_funnet(self):
        """Ugyldig trening_id gir SystemExit."""
        with self._patch_con():
            from use_case_3 import registrer_oppmote
            with self.assertRaises(SystemExit):
                registrer_oppmote("johnny@test.no", 999)

    def test_ikke_påmeldt(self):
        """Bruker som ikke er påmeldt treningen gir SystemExit."""
        # Profil 2 er IKKE lagt inn i påmeldt_til
        with self._patch_con():
            from use_case_3 import registrer_oppmote
            with self.assertRaises(SystemExit):
                registrer_oppmote("johnny@test.no", 1)

    def test_oppmøte_etter_slutt(self):
        """Registrering av oppmøte etter aktivitetens slutt avvises."""
        # Aktivitet som sluttet for 10 minutter siden
        self.con.execute(
            """INSERT INTO Gruppeaktivitet
               (senter_ID, sal_ID, ID, start, slutt, dato, aktivitet_navn, instrukt_ID)
               VALUES (1,1,2,
                       strftime('%H:%M', datetime('now','localtime','-70 minutes')),
                       strftime('%H:%M', datetime('now','localtime','-10 minutes')),
                       date('now','localtime'),
                       'Spin60', 1)"""
        )
        self.con.execute("INSERT INTO påmeldt_til VALUES (1,1,2,2,1)")
        self.con.commit()
        with self._patch_con():
            from use_case_3 import registrer_oppmote
            with self.assertRaises((SystemExit, sqlite3.OperationalError)):
                registrer_oppmote("johnny@test.no", 2)


class TestUkeplan(unittest.TestCase):
    """Tester brukstilfelle 4 – ukeplan."""

    def setUp(self):
        self.con = build_db()
        self.con.executescript("""
            INSERT INTO Senter (ID, navn, gate, nummer, fra, til)
                VALUES (1, 'TestSenter', 'Testgate', '1', '06:00', '22:00');

            INSERT INTO Sal (senter_ID, ID, type, kapasitet)
                VALUES (1, 1, 'spinning', 20);

            INSERT INTO Aktivitet (navn, kategori)
                VALUES ('Spin60', 'Spin');

            INSERT INTO Profil (ID, type, fornavn, etternavn, epost, telefon)
                VALUES (1, 'ansatt', 'Hanne', 'Fjeld', 'hanne@test.no', '90000001');

            INSERT INTO Gruppeaktivitet
                (senter_ID, sal_ID, ID, start, slutt, dato, aktivitet_navn, instrukt_ID)
            VALUES
                (1, 1, 1, '10:00', '11:00', '2030-01-01', 'Spin60', 1),
                (1, 1, 2, '12:00', '13:00', '2030-01-02', 'Spin60', 1);
        """)

    def tearDown(self):
        self.con.close()

    def test_ukeplan_viser_dato_per_kt(self):
        with patch("use_case_4.get_connection", return_value=self.con), patch("sys.stdout", new_callable=StringIO) as stdout:
            from use_case_4 import ukeplan
            ukeplan("2030-01-01", 1)

        output = stdout.getvalue()
        self.assertIn("2030-01-01 | Spin60 | 10:00-11:00 | TestSenter | sal 1", output)
        self.assertIn("2030-01-02 | Spin60 | 12:00-13:00 | TestSenter | sal 1", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
