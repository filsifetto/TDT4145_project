-- TDT4145 Prosjekt – Testdata
-- Kjøres mot en tom database etter create_tables.sql
--
-- Merk: lukkingstid '00:00' (midnatt) lagres som '24:00' slik at
--       CHECK (fra < til) i Senter-tabellen overholdes.

PRAGMA foreign_keys = ON;

-- ════════════════════════════════════════════════════════════════════════════
-- Senter
-- ════════════════════════════════════════════════════════════════════════════

INSERT INTO Senter (ID, navn, gate, nummer, fra, til) VALUES
    (1, 'Øya treningssenter',      'Vangslundsgate',        '2',  '05:00', '24:00'),
    (2, 'Dragvoll idrettssenter',  'Loholt allé',           '81', '05:00', '24:00'),
    (3, 'Gløshaugen idrettsbygg',  'Chr. Frederiks gate',   '20', '05:00', '24:00'),
    (4, 'Moholt treningssenter',   'Moholt allmenning',     '12', '05:00', '24:00'),
    (5, 'DMMH treningsrom',        'Thrond Nergaards veg',  '7',  '06:00', '23:30');

-- ════════════════════════════════════════════════════════════════════════════
-- Fasiliteter  (type, beskrivelse)
-- Kun for Øya treningssenter, jf. oppgavebeskrivelsen.
-- ════════════════════════════════════════════════════════════════════════════

INSERT INTO Fasilitet (ID, type, beskrivelse) VALUES
    (1, 'garderobe', 'Herregarderobe med låsbare skap'),
    (2, 'garderobe', 'Damegarderobe med låsbare skap'),
    (3, 'dusj',      'Herredusjrom med varmtvann'),
    (4, 'dusj',      'Damedusjrom med varmtvann'),
    (5, 'badstue',   'Finsk badstue');

-- Øya treningssenter (senter 1) har alle fasiliteter
INSERT INTO har_fasilitet (senter_ID, fasilitet_ID) VALUES
    (1, 1), (1, 2), (1, 3), (1, 4), (1, 5);

-- ════════════════════════════════════════════════════════════════════════════
-- Saler  (senter_ID, ID, type, kapasitet)
-- Fasiliteter, saler og sykler settes kun inn for Øya treningssenter.
-- For Dragvoll legges kun spinning-salen inn (nødvendig for gruppeaktiviteter).
-- ════════════════════════════════════════════════════════════════════════════

-- Øya treningssenter (5 saler)
INSERT INTO Sal (senter_ID, ID, type, kapasitet) VALUES
    (1, 1, 'spinning', 20),
    (1, 2, 'styrke',   30),
    (1, 3, 'cardio',   25),
    (1, 4, 'dans',     30),
    (1, 5, 'yoga',     20);

-- Dragvoll idrettssenter – kun spinning-sal (trengs for gruppeaktiviteter)
INSERT INTO Sal (senter_ID, ID, type, kapasitet) VALUES
    (2, 1, 'spinning', 16);

-- ════════════════════════════════════════════════════════════════════════════
-- Sykler  (senter_ID, sal_ID, nummer, bluetooth)
-- bluetooth: 1 = BodyBike-tilkobling, 0 = vanlig sykkel
-- Kun for Øya treningssenter (sal 1, spinning).
-- ════════════════════════════════════════════════════════════════════════════

-- Øya spinning-sal: 20 sykler – nr 1-12 med bluetooth, 13-20 uten
INSERT INTO Sykkel (senter_ID, sal_ID, nummer, bluetooth) VALUES
    (1, 1,  1, 1), (1, 1,  2, 1), (1, 1,  3, 1), (1, 1,  4, 1),
    (1, 1,  5, 1), (1, 1,  6, 1), (1, 1,  7, 1), (1, 1,  8, 1),
    (1, 1,  9, 1), (1, 1, 10, 1), (1, 1, 11, 1), (1, 1, 12, 1),
    (1, 1, 13, 0), (1, 1, 14, 0), (1, 1, 15, 0), (1, 1, 16, 0),
    (1, 1, 17, 0), (1, 1, 18, 0), (1, 1, 19, 0), (1, 1, 20, 0);

-- ════════════════════════════════════════════════════════════════════════════
-- Aktivitetstyper  (navn PK, kategori, beskrivelse)
-- Alle fire spinning-typer fra SiTs nettsider
-- ════════════════════════════════════════════════════════════════════════════

INSERT INTO Aktivitet (navn, kategori, beskrivelse) VALUES
    ('Spin 4x4',
     'Spin',
     'Intervalltime på sykkel med god oppvarming, deretter 4 stående intervaller på 4 minutter med ca 2 minutter aktiv pause mellom hvert drag. Timen avsluttes med nedsykling.'),
    ('Spin 8x3min',
     'Spin',
     'Intervalltime på sykkel der du jobber i intervaller på 3 minutter og kjører annethvert drag stående og sittende. Totalt 8 intervaller, med 1,5–2 min pause mellom. Oppvarming og nedtrapping er inkludert i timen.'),
    ('Spin45',
     'Spin',
     'Spinningtime med variert løype fordelt på 2–3 arbeidsperioder som passer for alle. Du bestemmer selv intensiteten med hvor mye motstand du legger på.'),
    ('Spin60',
     'Spin',
     'Spinningtime med variert løype fordelt på 2–4 arbeidsperioder. Litt raskere tempo og lengre stående perioder enn Spin45, men du bestemmer selv intensiteten.');

-- ════════════════════════════════════════════════════════════════════════════
-- Profiler  (type, fornavn, etternavn, epost, telefon)
-- ════════════════════════════════════════════════════════════════════════════

-- Prosjektgruppen (type = 'medlem')
INSERT INTO Profil (type, fornavn, etternavn, epost, telefon) VALUES
    ('medlem', 'Leo',   'Egilson Skarbø', 'leoes@stud.ntnu.no',    '94000001'),
    ('medlem', 'Knut',  'Opland Moen',    'knutomoe@stud.ntnu.no', '94000002'),
    ('medlem', 'Axel',  'Filseth',        'axelfi@stud.ntnu.no',   '94000003');

-- Johnny (brukes i oppgavens brukstilfeller)
INSERT INTO Profil (type, fornavn, etternavn, epost, telefon) VALUES
    ('medlem', 'Johnny', 'Olsen', 'johnny@stud.ntnu.no', '94000004');

-- Øvrige studenter
INSERT INTO Profil (type, fornavn, etternavn, epost, telefon) VALUES
    ('medlem', 'Emma',    'Bakke',       'emmab@stud.ntnu.no',    '94000005'),
    ('medlem', 'Sofie',   'Halvorsen',   'sofieh@stud.ntnu.no',   '94000006'),
    ('medlem', 'Mikkel',  'Strand',      'mikkels@stud.ntnu.no',  '94000007'),
    ('medlem', 'Ingrid',  'Dahl',        'ingrid@stud.ntnu.no',   '94000008'),
    ('medlem', 'Anders',  'Nygaard',     'andersn@stud.ntnu.no',  '94000009'),
    ('medlem', 'Maja',    'Eriksen',     'majae@stud.ntnu.no',    '94000010'),
    ('medlem', 'Tobias',  'Vesterås',    'tobiasv@stud.ntnu.no',  '94000011');

-- Ansatte / instruktører
INSERT INTO Profil (type, fornavn, etternavn, epost, telefon) VALUES
    ('ansatt', 'Hanne',  'Fjeld',   'hanne.fjeld@sit.no',   '90000001'),
    ('ansatt', 'Torben', 'Vik',     'torben.vik@sit.no',    '90000002'),
    ('ansatt', 'Silje',  'Aune',    'silje.aune@sit.no',    '90000003'),
    ('ansatt', 'Morten', 'Lunde',   'morten.lunde@sit.no',  '90000004');

-- ════════════════════════════════════════════════════════════════════════════
-- Gruppeaktiviteter  16.–18. mars 2026
-- Kun spinning på Øya (senter 1, sal 1) og Dragvoll (senter 2, sal 1).
-- BT2 krever Spin60 tirsdag 17. mars kl. 18:30 på Øya → ID=7 nedenfor.
-- Instruktører: Hanne=12, Torben=13, Silje=14, Morten=15
-- ════════════════════════════════════════════════════════════════════════════

-- Øya – mandag 16. mars
INSERT INTO Gruppeaktivitet (senter_ID, sal_ID, ID, start, slutt, dato, aktivitet_navn, instrukt_ID) VALUES
    (1, 1,  1, '07:00', '08:00', '2026-03-16', 'Spin60',     12),
    (1, 1,  2, '12:00', '12:45', '2026-03-16', 'Spin45',     13),
    (1, 1,  3, '17:00', '17:55', '2026-03-16', 'Spin 8x3min',14),
    (1, 1,  4, '18:30', '19:15', '2026-03-16', 'Spin 4x4',   15);

-- Øya – tirsdag 17. mars
INSERT INTO Gruppeaktivitet (senter_ID, sal_ID, ID, start, slutt, dato, aktivitet_navn, instrukt_ID) VALUES
    (1, 1,  5, '06:30', '07:15', '2026-03-17', 'Spin45',     12),
    (1, 1,  6, '12:00', '12:45', '2026-03-17', 'Spin 4x4',   13),
    (1, 1,  7, '18:30', '19:30', '2026-03-17', 'Spin60',     14);  -- Brukstilfelle 2

-- Øya – onsdag 18. mars
INSERT INTO Gruppeaktivitet (senter_ID, sal_ID, ID, start, slutt, dato, aktivitet_navn, instrukt_ID) VALUES
    (1, 1,  8, '07:00', '07:55', '2026-03-18', 'Spin 8x3min',15),
    (1, 1,  9, '17:00', '17:45', '2026-03-18', 'Spin45',     12),
    (1, 1, 10, '18:30', '19:15', '2026-03-18', 'Spin 4x4',   13);

-- Dragvoll – mandag 16. mars
INSERT INTO Gruppeaktivitet (senter_ID, sal_ID, ID, start, slutt, dato, aktivitet_navn, instrukt_ID) VALUES
    (2, 1,  1, '08:00', '08:45', '2026-03-16', 'Spin45',     13),
    (2, 1,  2, '17:30', '18:30', '2026-03-16', 'Spin60',     15);

-- Dragvoll – tirsdag 17. mars
INSERT INTO Gruppeaktivitet (senter_ID, sal_ID, ID, start, slutt, dato, aktivitet_navn, instrukt_ID) VALUES
    (2, 1,  3, '07:00', '07:45', '2026-03-17', 'Spin 4x4',   15),
    (2, 1,  4, '12:00', '12:45', '2026-03-17', 'Spin45',     14),
    (2, 1,  5, '18:00', '18:55', '2026-03-17', 'Spin 8x3min',13);

-- Dragvoll – onsdag 18. mars
INSERT INTO Gruppeaktivitet (senter_ID, sal_ID, ID, start, slutt, dato, aktivitet_navn, instrukt_ID) VALUES
    (2, 1,  6, '08:00', '09:00', '2026-03-18', 'Spin60',     15),
    (2, 1,  7, '17:30', '18:15', '2026-03-18', 'Spin45',     13);

-- ════════════════════════════════════════════════════════════════════════════
-- Påmeldinger  (brukstilfelle 8 – treningspartnere)
-- Flere brukere meldes på de samme spinningtimene slik at
-- self-join-queriet i BT8 gir meningsfulle resultater.
--
--   Johnny (4): Øya GA 1, 7, 10
--   Emma   (5): Øya GA 1, 7, 10
--   Sofie  (6): Øya GA 1, 7
--   Mikkel (7): Øya GA 7, Dragvoll GA 3
-- ════════════════════════════════════════════════════════════════════════════

INSERT INTO påmeldt_til (senter_ID, sal_ID, gruppeaktivitet_ID, profil_ID, påmelding_nummer) VALUES
    (1, 1,  1, 4, 1),
    (1, 1,  1, 5, 2),
    (1, 1,  1, 6, 3),
    (1, 1,  7, 4, 1),
    (1, 1,  7, 5, 2),
    (1, 1,  7, 6, 3),
    (1, 1,  7, 7, 4),
    (1, 1, 10, 4, 1),
    (1, 1, 10, 5, 2),
    (2, 1,  3, 7, 1);

-- ════════════════════════════════════════════════════════════════════════════
-- Oppmøte  (brukstilfelle 8 – treningspartnere)
-- Registrerer at brukerne faktisk møtte opp.
-- ════════════════════════════════════════════════════════════════════════════

INSERT INTO møter_til_gruppe (senter_ID, sal_ID, gruppeaktivitet_ID, profil_ID, tidspunkt) VALUES
    (1, 1,  1, 4, '2026-03-16 06:55'),
    (1, 1,  1, 5, '2026-03-16 06:56'),
    (1, 1,  1, 6, '2026-03-16 06:57'),
    (1, 1,  7, 4, '2026-03-17 18:25'),
    (1, 1,  7, 5, '2026-03-17 18:26'),
    (1, 1,  7, 6, '2026-03-17 18:27'),
    (1, 1,  7, 7, '2026-03-17 18:28'),
    (1, 1, 10, 4, '2026-03-18 18:25'),
    (1, 1, 10, 5, '2026-03-18 18:26'),
    (2, 1,  3, 7, '2026-03-17 06:55');
