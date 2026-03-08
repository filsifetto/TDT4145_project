-- TDT4145 Prosjektoppgave – SQL-script (oppgave c)
-- Oppretter alle tabeller med primær-/fremmednøkler og restriksjoner.
--
-- Målplattform: SQLite  (PRAGMA foreign_keys = ON må kjøres per tilkobling)
--
-- ============================================================================
-- Restriksjoner som IKKE kan uttrykkes i SQL og må håndteres i applikasjonskode:
--
--   1. Prikk ved manglende/for sen oppmøte: En profil som er påmeldt en
--      gruppeaktivitet uten å registrere oppmøte senest 5 minutter før start
--      skal få en prikk. Regelen krever tidsberegning utenfor databasen.
--
--   2. 48-timersregelen: En gruppetime skal legges ut 48 timer før den
--      holdes. Regelen er en myk forretningsregel som best håndheves i
--      applikasjonskoden, da en hard constraint ville hindret instruktører
--      som er noe forsinket fra å legge ut timer.
--
-- Restriksjoner håndhevet med triggere (se nederst i filen):
--
--   2. Utestengelse (svartelisting): >= 3 prikker siste 30 dager blokkerer
--      ny påmelding (check_utestengelse_insert).
--   3. Oppmøte etter aktivitetens slutt
--   4. Én booking per sal per tidspunkt (4 triggere: insert/update x 2 tabeller)
--   5. Medlemskap for idrettslagstime
--   6. Avbestillingsfrist (senest 1 time før start)
--   7. Instruktørrolle (kun ansatte kan settes som instruktør)
--   8. En instruktør kan ikke lede to gruppeaktiviteter som overlapper i tid
--      (check_instruktør_overlapp_insert/update)
--   9. En bruker kan ikke være påmeldt to gruppeaktiviteter som overlapper i tid
--      (check_bruker_overlapp_påmeldt_insert/update)
--  10. Kapasitetsgrense: Påmelding til gruppeaktivitet avslås når antall
--      påmeldte = salens kapasitet (check_kapasitet_påmeldt_insert)
--  11. Kapasitetsgrense dropin: Oppmøte til idrettslagstime avslås når
--      antall oppmøtte = salens kapasitet (check_kapasitet_idrett_insert)
--
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ════════════════════════════════════════════════════════════════════════════
-- Sterke entiteter
-- ════════════════════════════════════════════════════════════════════════════

CREATE TABLE Fasilitet (
    ID          INTEGER PRIMARY KEY AUTOINCREMENT,
    type        TEXT    NOT NULL,
    beskrivelse TEXT
);

CREATE TABLE Senter (
    ID     INTEGER PRIMARY KEY AUTOINCREMENT,
    navn   TEXT    NOT NULL UNIQUE,
    gate   TEXT    NOT NULL,
    nummer TEXT    NOT NULL,
    fra    TIME    NOT NULL,
    til    TIME    NOT NULL,
    CHECK (fra < til)
);

CREATE TABLE Idrettslag (
    ID          INTEGER PRIMARY KEY AUTOINCREMENT,
    navn        TEXT    NOT NULL,
    beskrivelse TEXT
);

CREATE TABLE Profil (
    ID       INTEGER PRIMARY KEY AUTOINCREMENT,
    type     TEXT    NOT NULL CHECK (type IN ('medlem', 'ansatt')),
    fornavn  TEXT    NOT NULL,
    etternavn TEXT   NOT NULL,
    epost    TEXT    NOT NULL UNIQUE,
    telefon  TEXT    NOT NULL UNIQUE
);

CREATE TABLE Aktivitet (
    navn        TEXT PRIMARY KEY,
    kategori    TEXT NOT NULL,
    beskrivelse TEXT
);

-- ════════════════════════════════════════════════════════════════════════════
-- Svake entiteter og M:N-relasjoner
-- ════════════════════════════════════════════════════════════════════════════

CREATE TABLE har_fasilitet (
    senter_ID    INTEGER NOT NULL,
    fasilitet_ID INTEGER NOT NULL,
    PRIMARY KEY (senter_ID, fasilitet_ID),
    FOREIGN KEY (senter_ID)    REFERENCES Senter(ID)    ON DELETE CASCADE,
    FOREIGN KEY (fasilitet_ID) REFERENCES Fasilitet(ID) ON DELETE CASCADE
);

CREATE TABLE Bemanning (
    senter_ID INTEGER NOT NULL,
    dag       TEXT    NOT NULL CHECK (dag IN (
                  'mandag','tirsdag','onsdag','torsdag',
                  'fredag','lørdag','søndag')),
    start     TIME    NOT NULL,
    slutt     TIME    NOT NULL,
    PRIMARY KEY (senter_ID, dag),
    FOREIGN KEY (senter_ID) REFERENCES Senter(ID) ON DELETE CASCADE,
    CHECK (start < slutt)
);

CREATE TABLE Sal (
    senter_ID INTEGER NOT NULL,
    ID        INTEGER NOT NULL,
    type      TEXT    NOT NULL,
    kapasitet INTEGER NOT NULL CHECK (kapasitet > 0),
    PRIMARY KEY (senter_ID, ID),
    FOREIGN KEY (senter_ID) REFERENCES Senter(ID) ON DELETE CASCADE
);

CREATE TABLE Tredemølle (
    senter_ID      INTEGER NOT NULL,
    sal_ID         INTEGER NOT NULL,
    nummer         INTEGER NOT NULL,
    produsent      TEXT    NOT NULL,
    maks_hastighet REAL    NOT NULL CHECK (maks_hastighet > 0),
    maks_stigning  REAL    NOT NULL CHECK (maks_stigning  > 0),
    PRIMARY KEY (senter_ID, sal_ID, nummer),
    FOREIGN KEY (senter_ID, sal_ID) REFERENCES Sal(senter_ID, ID) ON DELETE CASCADE
);

CREATE TABLE Sykkel (
    senter_ID INTEGER NOT NULL,
    sal_ID    INTEGER NOT NULL,
    nummer    INTEGER NOT NULL,
    bluetooth INTEGER NOT NULL DEFAULT 0 CHECK (bluetooth IN (0, 1)),
    PRIMARY KEY (senter_ID, sal_ID, nummer),
    FOREIGN KEY (senter_ID, sal_ID) REFERENCES Sal(senter_ID, ID) ON DELETE CASCADE
);

CREATE TABLE Gruppe (
    idrettslags_ID INTEGER NOT NULL,
    ID             INTEGER NOT NULL,
    type           TEXT    NOT NULL,
    beskrivelse    TEXT,
    PRIMARY KEY (idrettslags_ID, ID),
    FOREIGN KEY (idrettslags_ID) REFERENCES Idrettslag(ID) ON DELETE CASCADE
);

CREATE TABLE Prikk (
    profil_ID INTEGER NOT NULL,
    ID        INTEGER NOT NULL,
    dato      DATE    NOT NULL,
    PRIMARY KEY (profil_ID, ID),
    FOREIGN KEY (profil_ID) REFERENCES Profil(ID) ON DELETE CASCADE
);

CREATE TABLE er_medlem (
    idrettslags_ID INTEGER NOT NULL,
    profil_ID      INTEGER NOT NULL,
    PRIMARY KEY (idrettslags_ID, profil_ID),
    FOREIGN KEY (idrettslags_ID) REFERENCES Idrettslag(ID) ON DELETE CASCADE,
    FOREIGN KEY (profil_ID)      REFERENCES Profil(ID)     ON DELETE CASCADE
);

CREATE TABLE Idrettslagstime (
    senter_ID      INTEGER NOT NULL,
    sal_ID         INTEGER NOT NULL,
    ID             INTEGER NOT NULL,
    type           TEXT    NOT NULL,
    start          TIME    NOT NULL,
    slutt          TIME    NOT NULL,
    dato           DATE    NOT NULL,
    beskrivelse    TEXT,
    idrettslags_ID INTEGER NOT NULL,
    gruppe_ID      INTEGER NOT NULL,
    PRIMARY KEY (senter_ID, sal_ID, ID),
    FOREIGN KEY (senter_ID, sal_ID)            REFERENCES Sal(senter_ID, ID)            ON DELETE CASCADE,
    FOREIGN KEY (idrettslags_ID)               REFERENCES Idrettslag(ID)               ON DELETE CASCADE,
    FOREIGN KEY (idrettslags_ID, gruppe_ID)    REFERENCES Gruppe(idrettslags_ID, ID)    ON DELETE CASCADE,
    CHECK (start < slutt)
);

CREATE TABLE møter_til_idrett (
    senter_ID          INTEGER NOT NULL,
    sal_ID             INTEGER NOT NULL,
    idrettslagstime_ID INTEGER NOT NULL,
    profil_ID          INTEGER NOT NULL,
    PRIMARY KEY (senter_ID, sal_ID, idrettslagstime_ID, profil_ID),
    FOREIGN KEY (senter_ID, sal_ID, idrettslagstime_ID)
        REFERENCES Idrettslagstime(senter_ID, sal_ID, ID) ON DELETE CASCADE,
    FOREIGN KEY (profil_ID) REFERENCES Profil(ID)         ON DELETE CASCADE
);

CREATE TABLE Gruppeaktivitet (
    senter_ID      INTEGER NOT NULL,
    sal_ID         INTEGER NOT NULL,
    ID             INTEGER NOT NULL,
    start          TIME    NOT NULL,
    slutt          TIME    NOT NULL,
    dato           DATE    NOT NULL,
    aktivitet_navn TEXT    NOT NULL,
    instrukt_ID    INTEGER NOT NULL,
    PRIMARY KEY (senter_ID, sal_ID, ID),
    FOREIGN KEY (senter_ID, sal_ID) REFERENCES Sal(senter_ID, ID) ON DELETE CASCADE,
    FOREIGN KEY (aktivitet_navn)    REFERENCES Aktivitet(navn),
    FOREIGN KEY (instrukt_ID)       REFERENCES Profil(ID),
    CHECK (start < slutt)
);

CREATE TABLE møter_til_gruppe (
    senter_ID          INTEGER NOT NULL,
    sal_ID             INTEGER NOT NULL,
    gruppeaktivitet_ID INTEGER NOT NULL,
    profil_ID          INTEGER NOT NULL,
    tidspunkt          DATETIME NOT NULL,
    PRIMARY KEY (senter_ID, sal_ID, gruppeaktivitet_ID, profil_ID),
    FOREIGN KEY (senter_ID, sal_ID, gruppeaktivitet_ID)
        REFERENCES Gruppeaktivitet(senter_ID, sal_ID, ID) ON DELETE CASCADE,
    FOREIGN KEY (profil_ID) REFERENCES Profil(ID)         ON DELETE CASCADE
);

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
    FOREIGN KEY (profil_ID) REFERENCES Profil(ID)         ON DELETE CASCADE
);

-- ============================================================================
-- Triggere
-- ============================================================================

CREATE TRIGGER check_møter_til_gruppe_etter_slutt
BEFORE INSERT ON møter_til_gruppe
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Kan ikke registrere oppmøte etter gruppeaktivitetens slutt.')
    WHERE NEW.tidspunkt > (
        SELECT dato || ' ' || slutt
        FROM Gruppeaktivitet
        WHERE senter_ID = NEW.senter_ID
          AND sal_ID    = NEW.sal_ID
          AND ID        = NEW.gruppeaktivitet_ID
    );
END;

CREATE TRIGGER check_møter_til_idrett_etter_slutt
BEFORE INSERT ON møter_til_idrett
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Kan ikke registrere oppmøte etter idrettslagstime er ferdig.')
    WHERE datetime('now', 'localtime') > (
        SELECT dato || ' ' || slutt
        FROM Idrettslagstime
        WHERE senter_ID = NEW.senter_ID
          AND sal_ID    = NEW.sal_ID
          AND ID        = NEW.idrettslagstime_ID
    );
END;

CREATE TRIGGER check_sal_booking_gruppe_insert
BEFORE INSERT ON Gruppeaktivitet
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Salen er allerede booket av en gruppeaktivitet i dette tidsrommet.')
    WHERE EXISTS (
        SELECT 1 FROM Gruppeaktivitet
        WHERE senter_ID = NEW.senter_ID
          AND sal_ID    = NEW.sal_ID
          AND dato      = NEW.dato
          AND NEW.start < slutt
          AND NEW.slutt > start
    );
    SELECT RAISE(ABORT, 'Salen er allerede booket av en idrettslagstime i dette tidsrommet.')
    WHERE EXISTS (
        SELECT 1 FROM Idrettslagstime
        WHERE senter_ID = NEW.senter_ID
          AND sal_ID    = NEW.sal_ID
          AND dato      = NEW.dato
          AND NEW.start < slutt
          AND NEW.slutt > start
    );
END;

CREATE TRIGGER check_sal_booking_idrett_insert
BEFORE INSERT ON Idrettslagstime
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Salen er allerede booket av en gruppeaktivitet i dette tidsrommet.')
    WHERE EXISTS (
        SELECT 1 FROM Gruppeaktivitet
        WHERE senter_ID = NEW.senter_ID
          AND sal_ID    = NEW.sal_ID
          AND dato      = NEW.dato
          AND NEW.start < slutt
          AND NEW.slutt > start
    );
    SELECT RAISE(ABORT, 'Salen er allerede booket av en annen idrettslagstime i dette tidsrommet.')
    WHERE EXISTS (
        SELECT 1 FROM Idrettslagstime
        WHERE senter_ID = NEW.senter_ID
          AND sal_ID    = NEW.sal_ID
          AND dato      = NEW.dato
          AND NEW.start < slutt
          AND NEW.slutt > start
    );
END;

CREATE TRIGGER check_sal_booking_gruppe_update
BEFORE UPDATE ON Gruppeaktivitet
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Salen er allerede booket av en annen gruppeaktivitet i dette tidsrommet.')
    WHERE EXISTS (
        SELECT 1 FROM Gruppeaktivitet
        WHERE senter_ID = NEW.senter_ID
          AND sal_ID    = NEW.sal_ID
          AND dato      = NEW.dato
          AND NOT (senter_ID = NEW.senter_ID AND sal_ID = NEW.sal_ID AND ID = NEW.ID)
          AND NEW.start < slutt
          AND NEW.slutt > start
    );
    SELECT RAISE(ABORT, 'Salen er allerede booket av en idrettslagstime i dette tidsrommet.')
    WHERE EXISTS (
        SELECT 1 FROM Idrettslagstime
        WHERE senter_ID = NEW.senter_ID
          AND sal_ID    = NEW.sal_ID
          AND dato      = NEW.dato
          AND NEW.start < slutt
          AND NEW.slutt > start
    );
END;

CREATE TRIGGER check_sal_booking_idrett_update
BEFORE UPDATE ON Idrettslagstime
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Salen er allerede booket av en gruppeaktivitet i dette tidsrommet.')
    WHERE EXISTS (
        SELECT 1 FROM Gruppeaktivitet
        WHERE senter_ID = NEW.senter_ID
          AND sal_ID    = NEW.sal_ID
          AND dato      = NEW.dato
          AND NEW.start < slutt
          AND NEW.slutt > start
    );
    SELECT RAISE(ABORT, 'Salen er allerede booket av en annen idrettslagstime i dette tidsrommet.')
    WHERE EXISTS (
        SELECT 1 FROM Idrettslagstime
        WHERE senter_ID = NEW.senter_ID
          AND sal_ID    = NEW.sal_ID
          AND dato      = NEW.dato
          AND NOT (senter_ID = NEW.senter_ID AND sal_ID = NEW.sal_ID AND ID = NEW.ID)
          AND NEW.start < slutt
          AND NEW.slutt > start
    );
END;

CREATE TRIGGER check_medlemskap_idrett_insert
BEFORE INSERT ON møter_til_idrett
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Profil må være medlem av idrettslaget for å møte til idrettslagstime.')
    WHERE NOT EXISTS (
        SELECT 1 FROM er_medlem em
        JOIN Idrettslagstime it ON it.idrettslags_ID = em.idrettslags_ID
        WHERE it.senter_ID = NEW.senter_ID
          AND it.sal_ID    = NEW.sal_ID
          AND it.ID        = NEW.idrettslagstime_ID
          AND em.profil_ID = NEW.profil_ID
    );
END;

CREATE TRIGGER check_medlemskap_idrett_update
BEFORE UPDATE ON møter_til_idrett
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Profil må være medlem av idrettslaget for å møte til idrettslagstime.')
    WHERE NOT EXISTS (
        SELECT 1 FROM er_medlem em
        JOIN Idrettslagstime it ON it.idrettslags_ID = em.idrettslags_ID
        WHERE it.senter_ID = NEW.senter_ID
          AND it.sal_ID    = NEW.sal_ID
          AND it.ID        = NEW.idrettslagstime_ID
          AND em.profil_ID = NEW.profil_ID
    );
END;

CREATE TRIGGER check_avbestillingsfrist
BEFORE DELETE ON påmeldt_til
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Avbestilling må skje senest 1 time før aktivitetens start.')
    WHERE datetime('now', 'localtime') > (
        SELECT datetime(dato || ' ' || start, '-1 hour')
        FROM Gruppeaktivitet
        WHERE senter_ID = OLD.senter_ID
          AND sal_ID    = OLD.sal_ID
          AND ID        = OLD.gruppeaktivitet_ID
    );
END;

CREATE TRIGGER check_instruktør_rolle_insert
BEFORE INSERT ON Gruppeaktivitet
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Instruktør må ha type ansatt.')
    WHERE (SELECT type FROM Profil WHERE ID = NEW.instrukt_ID) != 'ansatt';
END;

CREATE TRIGGER check_instruktør_rolle_update
BEFORE UPDATE ON Gruppeaktivitet
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Instruktør må ha type ansatt.')
    WHERE (SELECT type FROM Profil WHERE ID = NEW.instrukt_ID) != 'ansatt';
END;

CREATE TRIGGER check_instruktør_overlapp_insert
BEFORE INSERT ON Gruppeaktivitet
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Instruktøren leder allerede en annen gruppeaktivitet som overlapper i tid.')
    WHERE EXISTS (
        SELECT 1 FROM Gruppeaktivitet
        WHERE instrukt_ID = NEW.instrukt_ID
          AND dato        = NEW.dato
          AND NEW.start   < slutt
          AND NEW.slutt   > start
    );
END;

CREATE TRIGGER check_instruktør_overlapp_update
BEFORE UPDATE ON Gruppeaktivitet
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Instruktøren leder allerede en annen gruppeaktivitet som overlapper i tid.')
    WHERE EXISTS (
        SELECT 1 FROM Gruppeaktivitet
        WHERE instrukt_ID = NEW.instrukt_ID
          AND dato        = NEW.dato
          AND NOT (senter_ID = NEW.senter_ID AND sal_ID = NEW.sal_ID AND ID = NEW.ID)
          AND NEW.start   < slutt
          AND NEW.slutt   > start
    );
END;


CREATE TRIGGER check_bruker_overlapp_påmeldt_insert
BEFORE INSERT ON påmeldt_til
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Profilen er allerede påmeldt en annen gruppeaktivitet som overlapper i tid.')
    WHERE EXISTS (
        SELECT 1
        FROM påmeldt_til pt
        JOIN Gruppeaktivitet ny  ON  ny.senter_ID = NEW.senter_ID
                                 AND ny.sal_ID    = NEW.sal_ID
                                 AND ny.ID        = NEW.gruppeaktivitet_ID
        JOIN Gruppeaktivitet eks ON eks.senter_ID = pt.senter_ID
                                 AND eks.sal_ID   = pt.sal_ID
                                 AND eks.ID       = pt.gruppeaktivitet_ID
        WHERE pt.profil_ID = NEW.profil_ID
          AND NOT (pt.senter_ID          = NEW.senter_ID
               AND pt.sal_ID             = NEW.sal_ID
               AND pt.gruppeaktivitet_ID = NEW.gruppeaktivitet_ID)
          AND eks.dato = ny.dato
          AND ny.start < eks.slutt
          AND ny.slutt > eks.start
    );
END;

CREATE TRIGGER check_bruker_overlapp_påmeldt_update
BEFORE UPDATE ON påmeldt_til
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Profilen er allerede påmeldt en annen gruppeaktivitet som overlapper i tid.')
    WHERE EXISTS (
        SELECT 1
        FROM påmeldt_til pt
        JOIN Gruppeaktivitet ny  ON  ny.senter_ID = NEW.senter_ID
                                 AND ny.sal_ID    = NEW.sal_ID
                                 AND ny.ID        = NEW.gruppeaktivitet_ID
        JOIN Gruppeaktivitet eks ON eks.senter_ID = pt.senter_ID
                                 AND eks.sal_ID   = pt.sal_ID
                                 AND eks.ID       = pt.gruppeaktivitet_ID
        WHERE pt.profil_ID = NEW.profil_ID
          AND NOT (pt.senter_ID          = NEW.senter_ID
               AND pt.sal_ID             = NEW.sal_ID
               AND pt.gruppeaktivitet_ID = NEW.gruppeaktivitet_ID)
          AND eks.dato = ny.dato
          AND ny.start < eks.slutt
          AND ny.slutt > eks.start
    );
END;

CREATE TRIGGER check_utestengelse_insert
BEFORE INSERT ON påmeldt_til
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Profilen er utestengt fra nettbooking: 3 eller flere prikker de siste 30 dagene.')
    WHERE (
        SELECT COUNT(*) FROM Prikk
        WHERE profil_ID = NEW.profil_ID
          AND dato >= date('now', 'localtime', '-30 days')
    ) >= 3;
END;

CREATE TRIGGER check_utestengelse_update
BEFORE UPDATE ON påmeldt_til
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Profilen er utestengt fra nettbooking: 3 eller flere prikker de siste 30 dagene.')
    WHERE (
        SELECT COUNT(*) FROM Prikk
        WHERE profil_ID = NEW.profil_ID
          AND dato >= date('now', 'localtime', '-30 days')
    ) >= 3;
END;

CREATE TRIGGER check_kapasitet_påmeldt_insert
BEFORE INSERT ON påmeldt_til
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Gruppeaktiviteten er full – kapasitetsgrensen er nådd.')
    WHERE (
        SELECT COUNT(*) FROM påmeldt_til
        WHERE senter_ID          = NEW.senter_ID
          AND sal_ID             = NEW.sal_ID
          AND gruppeaktivitet_ID = NEW.gruppeaktivitet_ID
    ) >= (
        SELECT kapasitet FROM Sal
        WHERE senter_ID = NEW.senter_ID
          AND ID        = NEW.sal_ID
    );
END;

CREATE TRIGGER check_kapasitet_idrett_insert
BEFORE INSERT ON møter_til_idrett
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Idrettslagstimen er full – kapasitetsgrensen er nådd.')
    WHERE (
        SELECT COUNT(*) FROM møter_til_idrett
        WHERE senter_ID          = NEW.senter_ID
          AND sal_ID             = NEW.sal_ID
          AND idrettslagstime_ID = NEW.idrettslagstime_ID
    ) >= (
        SELECT kapasitet FROM Sal
        WHERE senter_ID = NEW.senter_ID
          AND ID        = NEW.sal_ID
    );
END;