DROP TRIGGER IF EXISTS sett_påmelding_nummer_insert;
DROP TRIGGER IF EXISTS check_avbestillingsfrist;
DROP TRIGGER IF EXISTS check_bruker_overlapp_idrett_insert;
DROP TRIGGER IF EXISTS check_bruker_overlapp_idrett_update;
DROP TRIGGER IF EXISTS check_bruker_overlapp_påmeldt_insert;
DROP TRIGGER IF EXISTS check_bruker_overlapp_påmeldt_update;
DROP TRIGGER IF EXISTS check_kapasitet_møter_gruppe_insert;
DROP TRIGGER IF EXISTS check_utestengelse_insert;
DROP TRIGGER IF EXISTS check_utestengelse_update;

ALTER TABLE påmeldt_til RENAME TO påmeldt_til_gammel;

CREATE TABLE påmeldt_til (
    senter_ID          INTEGER NOT NULL,
    sal_ID             INTEGER NOT NULL,
    gruppeaktivitet_ID INTEGER NOT NULL,
    profil_ID          INTEGER NOT NULL,
    påmelding_nummer   INTEGER CHECK (påmelding_nummer IS NULL OR påmelding_nummer > 0),
    PRIMARY KEY (senter_ID, sal_ID, gruppeaktivitet_ID, profil_ID),
    UNIQUE (senter_ID, sal_ID, gruppeaktivitet_ID, påmelding_nummer),
    FOREIGN KEY (senter_ID, sal_ID, gruppeaktivitet_ID)
        REFERENCES Gruppeaktivitet(senter_ID, sal_ID, ID) ON DELETE CASCADE,
    FOREIGN KEY (profil_ID) REFERENCES Profil(ID)         ON DELETE CASCADE
);

INSERT INTO påmeldt_til
    (senter_ID, sal_ID, gruppeaktivitet_ID, profil_ID, påmelding_nummer)
SELECT
    senter_ID, sal_ID, gruppeaktivitet_ID, profil_ID, påmelding_nummer
FROM påmeldt_til_gammel;

DROP TABLE påmeldt_til_gammel;

CREATE TRIGGER sett_påmelding_nummer_insert
AFTER INSERT ON påmeldt_til
FOR EACH ROW
WHEN NEW.påmelding_nummer IS NULL
BEGIN
    UPDATE påmeldt_til
    SET påmelding_nummer = (
        SELECT COALESCE(MAX(pt.påmelding_nummer), 0) + 1
        FROM påmeldt_til pt
        WHERE pt.senter_ID          = NEW.senter_ID
          AND pt.sal_ID             = NEW.sal_ID
          AND pt.gruppeaktivitet_ID = NEW.gruppeaktivitet_ID
          AND NOT (
              pt.senter_ID          = NEW.senter_ID
              AND pt.sal_ID         = NEW.sal_ID
              AND pt.gruppeaktivitet_ID = NEW.gruppeaktivitet_ID
              AND pt.profil_ID      = NEW.profil_ID
          )
    )
    WHERE senter_ID          = NEW.senter_ID
      AND sal_ID             = NEW.sal_ID
      AND gruppeaktivitet_ID = NEW.gruppeaktivitet_ID
      AND profil_ID          = NEW.profil_ID;
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
    SELECT RAISE(ABORT, 'Profilen er registrert på en idrettslagstime som overlapper i tid.')
    WHERE EXISTS (
        SELECT 1
        FROM møter_til_idrett mti
        JOIN Idrettslagstime it ON it.senter_ID = mti.senter_ID
                                AND it.sal_ID    = mti.sal_ID
                                AND it.ID        = mti.idrettslagstime_ID
        JOIN Gruppeaktivitet ga ON ga.senter_ID = NEW.senter_ID
                                AND ga.sal_ID    = NEW.sal_ID
                                AND ga.ID        = NEW.gruppeaktivitet_ID
        WHERE mti.profil_ID = NEW.profil_ID
          AND it.dato = ga.dato
          AND ga.start < it.slutt
          AND ga.slutt > it.start
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
    SELECT RAISE(ABORT, 'Profilen er registrert på en idrettslagstime som overlapper i tid.')
    WHERE EXISTS (
        SELECT 1
        FROM møter_til_idrett mti
        JOIN Idrettslagstime it ON it.senter_ID = mti.senter_ID
                                AND it.sal_ID    = mti.sal_ID
                                AND it.ID        = mti.idrettslagstime_ID
        JOIN Gruppeaktivitet ga ON ga.senter_ID = NEW.senter_ID
                                AND ga.sal_ID    = NEW.sal_ID
                                AND ga.ID        = NEW.gruppeaktivitet_ID
        WHERE mti.profil_ID = NEW.profil_ID
          AND it.dato = ga.dato
          AND ga.start < it.slutt
          AND ga.slutt > it.start
    );
END;

CREATE TRIGGER check_bruker_overlapp_idrett_insert
BEFORE INSERT ON møter_til_idrett
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Profilen er påmeldt en gruppeaktivitet som overlapper i tid.')
    WHERE EXISTS (
        SELECT 1
        FROM påmeldt_til pt
        JOIN Gruppeaktivitet ga ON ga.senter_ID = pt.senter_ID
                               AND ga.sal_ID    = pt.sal_ID
                               AND ga.ID        = pt.gruppeaktivitet_ID
        JOIN Idrettslagstime it ON it.senter_ID = NEW.senter_ID
                                AND it.sal_ID    = NEW.sal_ID
                                AND it.ID        = NEW.idrettslagstime_ID
        WHERE pt.profil_ID = NEW.profil_ID
          AND ga.dato = it.dato
          AND it.start < ga.slutt
          AND it.slutt > ga.start
    );
    SELECT RAISE(ABORT, 'Profilen er allerede registrert på en annen idrettslagstime som overlapper i tid.')
    WHERE EXISTS (
        SELECT 1
        FROM møter_til_idrett mti
        JOIN Idrettslagstime ny  ON ny.senter_ID = NEW.senter_ID
                                 AND ny.sal_ID    = NEW.sal_ID
                                 AND ny.ID        = NEW.idrettslagstime_ID
        JOIN Idrettslagstime eks ON eks.senter_ID = mti.senter_ID
                                 AND eks.sal_ID    = mti.sal_ID
                                 AND eks.ID        = mti.idrettslagstime_ID
        WHERE mti.profil_ID = NEW.profil_ID
          AND NOT (mti.senter_ID          = NEW.senter_ID
               AND mti.sal_ID             = NEW.sal_ID
               AND mti.idrettslagstime_ID = NEW.idrettslagstime_ID)
          AND eks.dato = ny.dato
          AND ny.start < eks.slutt
          AND ny.slutt > eks.start
    );
END;

CREATE TRIGGER check_bruker_overlapp_idrett_update
BEFORE UPDATE ON møter_til_idrett
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Profilen er påmeldt en gruppeaktivitet som overlapper i tid.')
    WHERE EXISTS (
        SELECT 1
        FROM påmeldt_til pt
        JOIN Gruppeaktivitet ga ON ga.senter_ID = pt.senter_ID
                               AND ga.sal_ID    = pt.sal_ID
                               AND ga.ID        = pt.gruppeaktivitet_ID
        JOIN Idrettslagstime it ON it.senter_ID = NEW.senter_ID
                                AND it.sal_ID    = NEW.sal_ID
                                AND it.ID        = NEW.idrettslagstime_ID
        WHERE pt.profil_ID = NEW.profil_ID
          AND ga.dato = it.dato
          AND it.start < ga.slutt
          AND it.slutt > ga.start
    );
    SELECT RAISE(ABORT, 'Profilen er allerede registrert på en annen idrettslagstime som overlapper i tid.')
    WHERE EXISTS (
        SELECT 1
        FROM møter_til_idrett mti
        JOIN Idrettslagstime ny  ON ny.senter_ID = NEW.senter_ID
                                 AND ny.sal_ID    = NEW.sal_ID
                                 AND ny.ID        = NEW.idrettslagstime_ID
        JOIN Idrettslagstime eks ON eks.senter_ID = mti.senter_ID
                                 AND eks.sal_ID    = mti.sal_ID
                                 AND eks.ID        = mti.idrettslagstime_ID
        WHERE mti.profil_ID = NEW.profil_ID
          AND NOT (mti.senter_ID          = NEW.senter_ID
               AND mti.sal_ID             = NEW.sal_ID
               AND mti.idrettslagstime_ID = NEW.idrettslagstime_ID)
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

CREATE TRIGGER check_kapasitet_møter_gruppe_insert
BEFORE INSERT ON møter_til_gruppe
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Profilen er ikke blant de n første i ventelisten – kapasitetsgrensen er nådd.')
    WHERE (
        SELECT COUNT(*) FROM påmeldt_til
        WHERE senter_ID          = NEW.senter_ID
          AND sal_ID             = NEW.sal_ID
          AND gruppeaktivitet_ID = NEW.gruppeaktivitet_ID
          AND påmelding_nummer  <= (
              SELECT påmelding_nummer FROM påmeldt_til
              WHERE senter_ID          = NEW.senter_ID
                AND sal_ID             = NEW.sal_ID
                AND gruppeaktivitet_ID = NEW.gruppeaktivitet_ID
                AND profil_ID          = NEW.profil_ID
          )
    ) > (
        SELECT kapasitet FROM Sal
        WHERE senter_ID = NEW.senter_ID
          AND ID        = NEW.sal_ID
    );
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
