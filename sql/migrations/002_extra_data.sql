-- TDT4145 Prosjekt - Ekstra testdata (migrasjon 002)
-- Kjøres etter 001_insert_data.sql
-- Merk: rader som allerede finnes i 001_insert_data.sql er fjernet herfra.

PRAGMA foreign_keys = ON;

-- ============================================================================
-- Section 1 - Flere saler
-- ============================================================================

INSERT INTO Sal (senter_ID, ID, type, kapasitet) VALUES
    (3, 1, 'spinning', 20),
    (3, 2, 'yoga',     20),
    (3, 3, 'dans',     25),
    (4, 1, 'spinning', 18),
    (4, 2, 'styrke',   25),
    (5, 1, 'styrke',   15);

-- ============================================================================
-- Section 2 - Tredemøller
-- 5 tredemøller i Øya styrke-sal (1,2)
-- ============================================================================

INSERT INTO Tredemølle
    (senter_ID, sal_ID, nummer, produsent, maksimal_hastighet, maksimal_stigning)
VALUES
    (1, 2, 1, 'Technogym',   22.0, 15.0),
    (1, 2, 2, 'Life Fitness',20.0, 15.0),
    (1, 2, 3, 'Technogym',   24.0, 16.0),
    (1, 2, 4, 'Life Fitness',20.0, 15.0),
    (1, 2, 5, 'Technogym',   22.0, 15.0);

-- ============================================================================
-- Section 3 - Bemanning
-- En rad per (senter, dag), kun hverdager
-- ============================================================================

INSERT INTO Bemanning (senter_ID, dag, start, slutt) VALUES
    (1, 'mandag',  '08:00', '20:00'),
    (1, 'tirsdag', '08:00', '20:00'),
    (1, 'onsdag',  '08:00', '20:00'),
    (1, 'torsdag', '08:00', '20:00'),
    (1, 'fredag',  '08:00', '20:00'),
    (2, 'mandag',  '08:00', '20:00'),
    (2, 'tirsdag', '08:00', '20:00'),
    (2, 'onsdag',  '08:00', '20:00'),
    (2, 'torsdag', '08:00', '20:00'),
    (2, 'fredag',  '08:00', '20:00'),
    (3, 'mandag',  '08:00', '20:00'),
    (3, 'tirsdag', '08:00', '20:00'),
    (3, 'onsdag',  '08:00', '20:00'),
    (3, 'torsdag', '08:00', '20:00'),
    (3, 'fredag',  '08:00', '20:00'),
    (4, 'mandag',  '08:00', '20:00'),
    (4, 'tirsdag', '08:00', '20:00'),
    (4, 'onsdag',  '08:00', '20:00'),
    (4, 'torsdag', '08:00', '20:00'),
    (4, 'fredag',  '08:00', '20:00'),
    (5, 'mandag',  '08:00', '19:00'),
    (5, 'tirsdag', '08:00', '19:00'),
    (5, 'onsdag',  '08:00', '19:00'),
    (5, 'torsdag', '08:00', '19:00'),
    (5, 'fredag',  '08:00', '19:00');

-- ============================================================================
-- Section 4 - Nye aktiviteter
-- ============================================================================

INSERT INTO Aktivitet (navn, kategori, beskrivelse) VALUES
    ('Yoga Flow',      'Yoga',      'Rolig flyt med fokus pa mobilitet og pust.'),
    ('Yoga Sterk',     'Yoga',      'Dynamisk yogatime med ekstra styrkefokus.'),
    ('Dans & Rytme',   'Dans',      'Dansetime med enkle kombinasjoner og hoy energi.'),
    ('Zumba',          'Dans',      'Kondisjonsdans inspirert av latinamerikanske rytmer.'),
    ('Styrketrening',  'Styrke',    'Helkroppstime med fokus pa basisovelser.'),
    ('HIIT',           'Kondisjon', 'Intervallokter med hoy intensitet og korte pauser.'),
    ('Pilates',        'Kondisjon', 'Kjerne, kontroll og utholdenhet i moderat tempo.');

-- ============================================================================
-- Section 5 - Nye profiler (ID 16-22)
-- ============================================================================

INSERT INTO Profil (ID, type, fornavn, etternavn, epost, telefon) VALUES
    (16, 'medlem', 'Nora',    'Solberg', 'nora.solberg@stud.ntnu.no',   '94000012'),
    (17, 'medlem', 'Lars',    'Berg',    'lars.berg@stud.ntnu.no',      '94000013'),
    (18, 'medlem', 'Ida',     'Nilsen',  'ida.nilsen@stud.ntnu.no',     '94000014'),
    (19, 'medlem', 'Sander',  'Lie',     'sander.lie@stud.ntnu.no',     '94000015'),
    (20, 'medlem', 'Julie',   'Hovden',  'julie.hovden@stud.ntnu.no',   '94000016'),
    (21, 'ansatt', 'Kristin', 'Haug',    'kristin.haug@sit.no',         '90000005'),
    (22, 'medlem', 'Ole',     'Svendsen','ole.svendsen@stud.ntnu.no',   '94000017');

-- ============================================================================
-- Section 6 - Idrettslag, grupper, medlemskap
-- ============================================================================

INSERT INTO Idrettslag (ID, navn, beskrivelse) VALUES
    (1, 'NTNUI',                       'Studentidrettslaget ved NTNU.'),
    (2, 'Studentidrettslaget Dragvoll', 'Idrettslag med base pa Dragvoll.');

INSERT INTO Gruppe (idrettslags_ID, ID, type, beskrivelse) VALUES
    (1, 1, 'Fotball',   'Fotballgruppe for studenter i Trondheim.'),
    (1, 2, 'Svomming',  'Svommegruppe med fokus pa teknikk og utholdenhet.'),
    (2, 1, 'Friidrett', 'Friidrettsgruppe med intervall og styrkeokter.');

INSERT INTO er_medlem (idrettslags_ID, profil_ID) VALUES
    (1, 4), (1, 5), (1, 6), (1, 7), (1, 16),
    (2, 8), (2, 9), (2, 17);

-- ============================================================================
-- Section 7 - Gruppeaktiviteter
-- Forrige uke: 2026-03-09 til 2026-03-12
-- Gjeldende uke ekstra: 2026-03-16 til 2026-03-20
-- ============================================================================

INSERT INTO Gruppeaktivitet
    (senter_ID, sal_ID, ID, start, slutt, dato, aktivitet_navn, instrukt_ID)
VALUES
    -- Forrige uke
    (1, 4, 1, '07:00', '08:00', '2026-03-09', 'Yoga Flow',      12),
    (1, 4, 2, '18:00', '19:00', '2026-03-10', 'Dans & Rytme',   13),
    (1, 5, 1, '16:00', '17:00', '2026-03-11', 'Yoga Sterk',     14),
    (4, 1, 1, '17:30', '18:30', '2026-03-11', 'Spin45',         21),
    (3, 1, 1, '07:30', '08:30', '2026-03-12', 'Spin 4x4',       15),

    -- Gjeldende uke ekstra
    (1, 5, 2, '09:00', '09:55', '2026-03-16', 'Yoga Flow',      21),
    (1, 4, 3, '15:00', '15:50', '2026-03-16', 'Dans & Rytme',   14),
    (4, 2, 1, '19:30', '20:20', '2026-03-16', 'Styrketrening',  21),
    (3, 2, 1, '09:00', '09:55', '2026-03-17', 'Yoga Sterk',     21),
    (3, 3, 1, '16:00', '16:50', '2026-03-17', 'Zumba',          12),
    (4, 2, 2, '18:00', '18:50', '2026-03-17', 'HIIT',           21),
    (1, 5, 3, '10:00', '10:55', '2026-03-18', 'Pilates',        21),
    (4, 2, 3, '16:00', '16:50', '2026-03-18', 'Styrketrening',  14),
    (3, 2, 2, '17:00', '17:55', '2026-03-19', 'Yoga Flow',      21),
    (1, 4, 4, '18:00', '18:50', '2026-03-19', 'Dans & Rytme',   13),
    (4, 2, 4, '07:00', '07:50', '2026-03-20', 'HIIT',           21),
    (3, 3, 2, '12:00', '12:50', '2026-03-20', 'Zumba',          15);

-- ============================================================================
-- Section 8 - Idrettslagstimer (fremtidige datoer)
-- ============================================================================

INSERT INTO Idrettslagstime
    (senter_ID, sal_ID, ID, type, start, slutt, dato, beskrivelse, idrettslags_ID, gruppe_ID)
VALUES
    (3, 2, 1, 'svomming teknikk',   '17:00', '18:00', '2026-03-23', 'Teknikkokt for svommegruppa.',     1, 2),
    (4, 1, 1, 'fotball fys',        '18:00', '19:00', '2026-03-24', 'Intervallokt for fotballgruppa.',  1, 1),
    (3, 1, 2, 'friidrett intervall','19:00', '20:00', '2026-03-25', 'Intervalltrening for friidrett.',  2, 1),
    (4, 2, 1, 'friidrett styrke',   '17:00', '18:00', '2026-03-26', 'Basestyrke for friidrett.',        2, 1);

-- ============================================================================
-- Section 9 - Påmeldinger
-- Kun NYE rader – profiler som allerede er påmeldt i 001_insert_data.sql er utelatt.
-- Påmelding_nummer er satt etter eksisterende numre fra 001_insert_data.sql.
--
--   GA 7 (Øya, 17. mars): profil 4(1), 5(2), 6(3), 7(4) fra insert_data → profil 8 får nr 5
--   GA 1 (Øya, 16. mars): profil 4(1), 5(2), 6(3) fra insert_data         → profil 10 får nr 4
-- ============================================================================

INSERT INTO påmeldt_til
    (senter_ID, sal_ID, gruppeaktivitet_ID, profil_ID, påmelding_nummer)
VALUES
    -- Øya 17. mars 18:30 (GA 7) – kun ny profil 8
    (1, 1, 7, 8, 5),

    -- Dragvoll 17. mars 18:00 (GA 5)
    (2, 1, 5, 9,  1),
    (2, 1, 5, 10, 2),
    (2, 1, 5, 11, 3),
    (2, 1, 5, 16, 4),

    -- Øya 18. mars 17:00 (GA 9)
    (1, 1, 9, 4, 1),
    (1, 1, 9, 8, 2),
    (1, 1, 9, 9, 3),

    -- Øya 16. mars 07:00 (GA 1) – kun ny profil 10
    (1, 1, 1, 10, 4);

-- ============================================================================
-- Section 10 - Historisk oppmøte (forrige uke)
-- Tidspunkt er satt innenfor aktivitetenes start/slutt-vindu
-- ============================================================================

INSERT INTO møter_til_gruppe
    (senter_ID, sal_ID, gruppeaktivitet_ID, profil_ID, tidspunkt)
VALUES
    -- 2026-03-09, (1,4,1) 07:00-08:00
    (1, 4, 1, 4,  '2026-03-09 07:30'),
    (1, 4, 1, 5,  '2026-03-09 07:35'),
    (1, 4, 1, 16, '2026-03-09 07:40'),

    -- 2026-03-10, (1,4,2) 18:00-19:00
    (1, 4, 2, 4,  '2026-03-10 18:20'),
    (1, 4, 2, 6,  '2026-03-10 18:25'),
    (1, 4, 2, 8,  '2026-03-10 18:30'),
    (1, 4, 2, 17, '2026-03-10 18:35'),

    -- 2026-03-11, (1,5,1) 16:00-17:00
    (1, 5, 1, 5,  '2026-03-11 16:20'),
    (1, 5, 1, 9,  '2026-03-11 16:25'),
    (1, 5, 1, 18, '2026-03-11 16:30'),

    -- 2026-03-11, (4,1,1) 17:30-18:30
    (4, 1, 1, 6,  '2026-03-11 17:50'),
    (4, 1, 1, 8,  '2026-03-11 18:00'),
    (4, 1, 1, 10, '2026-03-11 18:05'),

    -- 2026-03-12, (3,1,1) 07:30-08:30
    (3, 1, 1, 4,  '2026-03-12 07:50'),
    (3, 1, 1, 11, '2026-03-12 07:55'),
    (3, 1, 1, 16, '2026-03-12 08:00');

-- ============================================================================
-- Section 11 - Prikker
-- Profil  7 (Mikkel): 3 prikker siste 30 dager → svartelistet
-- Profil  8 (Ingrid): 2 prikker siste 30 dager → ikke svartelistet
-- Profil 22 (Ole):    4 prikker siste 30 dager → svartelistet
-- ============================================================================

INSERT INTO Prikk (profil_ID, ID, dato) VALUES
    (7, 1, '2026-02-20'),
    (7, 2, '2026-03-01'),
    (7, 3, '2026-03-10'),
    (8, 1, '2026-02-25'),
    (8, 2, '2026-03-05'),
    (22, 1, '2026-02-15'),
    (22, 2, '2026-02-22'),
    (22, 3, '2026-03-02'),
    (22, 4, '2026-03-10');
