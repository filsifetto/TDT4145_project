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
--      skal få en prikk.  Regelen krever tidsberegning og kan ikke fanges av
--      en enkel CHECK-restriksjon.
--
--   2. Utestengelse (svartelisting): Dersom en profil har >= 3 prikker
--      innenfor de siste 30 dagene, skal profilen utestenges fra elektronisk
--      booking inntil den eldste av de tre prikkene er eldre enn 30 dager.
--
--   4. Én booking per sal per tidspunkt: For et gitt tidspunkt kan en sal
--      kun ha én gruppeaktivitet eller én idrettslagstime.  Overlappsjekk
--      krever intervallsammenligning og kan ikke uttrykkes med UNIQUE alene.
--
--   5. Medlemskap for idrettslagstime: En profil må være medlem av
--      idrettslaget (via er_medlem) for å kunne møte til en idrettslagstime.
--
--   6. Avbestillingsfrist: Avbestilling av en gruppeaktivitet må skje senest
--      1 time før aktivitetens start.
--
--   7. Publiseringsfrist: En gruppeaktivitet legges ut for booking tidligst
--      48 timer før den holdes.
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
    fra    TIME   NOT NULL,
    til    TIME   NOT NULL
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
    FOREIGN KEY (senter_ID)    REFERENCES Senter(ID),
    FOREIGN KEY (fasilitet_ID) REFERENCES Fasilitet(ID)
);

CREATE TABLE Bemanning (
    senter_ID INTEGER NOT NULL,
    dag       TEXT    NOT NULL CHECK (dag IN (
                  'mandag','tirsdag','onsdag','torsdag',
                  'fredag','lørdag','søndag')),
    start     TIME    NOT NULL,
    slutt     TIME    NOT NULL,
    PRIMARY KEY (senter_ID, dag),
    FOREIGN KEY (senter_ID) REFERENCES Senter(ID),
    CHECK (start < slutt)
);

CREATE TABLE Sal (
    senter_ID INTEGER NOT NULL,
    ID        INTEGER NOT NULL,
    type      TEXT    NOT NULL,
    kapasitet INTEGER NOT NULL CHECK (kapasitet > 0),
    PRIMARY KEY (senter_ID, ID),
    FOREIGN KEY (senter_ID) REFERENCES Senter(ID)
);

CREATE TABLE Tredemølle (
    senter_ID      INTEGER NOT NULL,
    sal_ID         INTEGER NOT NULL,
    nummer         INTEGER NOT NULL,
    produsent      TEXT    NOT NULL,
    maks_hastighet REAL    NOT NULL CHECK (maks_hastighet > 0),
    maks_stigning  REAL    NOT NULL CHECK (maks_stigning  > 0),
    PRIMARY KEY (senter_ID, sal_ID, nummer),
    FOREIGN KEY (senter_ID, sal_ID) REFERENCES Sal(senter_ID, ID)
);

CREATE TABLE Sykkel (
    senter_ID INTEGER NOT NULL,
    sal_ID    INTEGER NOT NULL,
    nummer    INTEGER NOT NULL,
    bluetooth INTEGER NOT NULL DEFAULT 0 CHECK (bluetooth IN (0, 1)),
    PRIMARY KEY (senter_ID, sal_ID, nummer),
    FOREIGN KEY (senter_ID, sal_ID) REFERENCES Sal(senter_ID, ID)
);

CREATE TABLE Gruppe (
    idrettslags_ID INTEGER NOT NULL,
    ID             INTEGER NOT NULL,
    type           TEXT    NOT NULL,
    beskrivelse    TEXT,
    PRIMARY KEY (idrettslags_ID, ID),
    FOREIGN KEY (idrettslags_ID) REFERENCES Idrettslag(ID)
);

CREATE TABLE Prikk (
    profil_ID INTEGER NOT NULL,
    ID        INTEGER NOT NULL,
    dato      DATE    NOT NULL,
    PRIMARY KEY (profil_ID, ID),
    FOREIGN KEY (profil_ID) REFERENCES Profil(ID)
);

CREATE TABLE er_medlem (
    idrettslags_ID INTEGER NOT NULL,
    profil_ID      INTEGER NOT NULL,
    PRIMARY KEY (idrettslags_ID, profil_ID),
    FOREIGN KEY (idrettslags_ID) REFERENCES Idrettslag(ID),
    FOREIGN KEY (profil_ID)      REFERENCES Profil(ID)
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
    FOREIGN KEY (senter_ID, sal_ID)            REFERENCES Sal(senter_ID, ID),
    FOREIGN KEY (idrettslags_ID)               REFERENCES Idrettslag(ID),
    FOREIGN KEY (idrettslags_ID, gruppe_ID)    REFERENCES Gruppe(idrettslags_ID, ID),
    CHECK (start < slutt)
);

CREATE TABLE møter_til_idrett (
    senter_ID          INTEGER NOT NULL,
    sal_ID             INTEGER NOT NULL,
    idrettslagstime_ID INTEGER NOT NULL,
    profil_ID          INTEGER NOT NULL,
    PRIMARY KEY (senter_ID, sal_ID, idrettslagstime_ID, profil_ID),
    FOREIGN KEY (senter_ID, sal_ID, idrettslagstime_ID)
        REFERENCES Idrettslagstime(senter_ID, sal_ID, ID),
    FOREIGN KEY (profil_ID) REFERENCES Profil(ID)
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
    FOREIGN KEY (senter_ID, sal_ID) REFERENCES Sal(senter_ID, ID),
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
        REFERENCES Gruppeaktivitet(senter_ID, sal_ID, ID),
    FOREIGN KEY (profil_ID) REFERENCES Profil(ID)
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
        REFERENCES Gruppeaktivitet(senter_ID, sal_ID, ID),
    FOREIGN KEY (profil_ID) REFERENCES Profil(ID)
);

CREATE TRIGGER check_instruktør_rolle
BEFORE INSERT ON Gruppeaktivitet
FOR EACH ROW
BEGIN
    IF NEW.instrukt_ID NOT IN (SELECT ID FROM Profil WHERE type = 'ansatt') THEN
        RAISE (ABORT, 'Instruktør må være ansatt for å kunne settes som instruktør for en gruppeaktivitet.');
    END IF;
END;

CREATE TRIGGER check_medlemskap_idrett
BEFORE INSERT ON møter_til_idrett
FOR EACH ROW
BEGIN
    IF NEW.profil_ID NOT IN (SELECT profil_ID FROM er_medlem WHERE idrettslags_ID = NEW.idrettslags_ID) THEN
        RAISE (ABORT, 'Profilen må være medlem av idrettslaget for å kunne møte til en idrettslagstime.');
    END IF;
END;


create trigger check_instruktør_rolle_update
BEFORE UPDATE ON Gruppeaktivitet
FOR EACH ROW
BEGIN
    IF NEW.instrukt_ID NOT IN (SELECT ID FROM Profil WHERE type = 'ansatt') THEN
        RAISE (ABORT, 'Instruktør må være ansatt for å kunne settes som instruktør for en gruppeaktivitet.');
    END IF;
END;

CREATE TRIGGER check_medlemskap_idrett_update
BEFORE UPDATE ON møter_til_idrett
FOR EACH ROW
BEGIN
    IF NEW.profil_ID NOT IN (SELECT profil_ID FROM er_medlem WHERE idrettslags_ID = NEW.idrettslags_ID) THEN
        RAISE (ABORT, 'Profilen må være medlem av idrettslaget for å kunne møte til en idrettslagstime.');
    END IF;
END;

CREATE TRIGGER check_møter_til_idrett_time
BEFORE INSERT ON møter_til_idrett
FOR EACH ROW
BEGIN
    IF NEW.idrettslagstime_ID.slutt < NEW.tidspunkt THEN
        RAISE (ABORT, 'Møtet kan ikke være etter idrettslagstimenes slutt tidspunkt.');
    END IF;
END;

CREATE TRIGGER check_påmeldt_til_time
BEFORE INSERT ON påmeldt_til
FOR EACH ROW
BEGIN
    IF NEW.gruppeaktivitet_ID.slutt < NEW.tidspunkt THEN
        RAISE (ABORT, 'Påmeldingen kan ikke være etter gruppeaktivitetens slutt tidspunkt.');
    END IF;
END;