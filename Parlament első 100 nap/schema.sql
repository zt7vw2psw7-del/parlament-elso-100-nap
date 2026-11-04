-- =====================================================================
-- PARLAMENTI FELSZÓLALÁSOK ÉS KÉRDÉSEK ADATBÁZISA (2010 ÉS 2026 ELSŐ 100 NAP)
-- =====================================================================

PRAGMA foreign_keys = ON;

-- 1. KORSZAKOK (2010 vs 2026)
CREATE TABLE IF NOT EXISTS period (
    id TEXT PRIMARY KEY,                   -- pl. '2010', '2026'
    name TEXT NOT NULL,                   -- pl. '2010-es kormányváltás', '2026-os kormányváltás'
    inaugural_date DATE NOT NULL,         -- Alakuló ülés dátuma (2010-05-14 / 2026-05-09)
    end_date DATE NOT NULL,               -- +100 napos határidő (2010-08-22 / 2026-08-17)
    description TEXT
);

-- 2. KÉPVISELŐCSOPORTOK / FRAKCIÓK
CREATE TABLE IF NOT EXISTS parliamentary_group (
    id TEXT PRIMARY KEY,                   -- pl. '2010_FIDESZ', '2026_TISZA', stb.
    period_id TEXT NOT NULL,              -- '2010' vagy '2026'
    code TEXT NOT NULL,                   -- pl. 'FIDESZ', 'KDNP', 'MSZP', 'JOBBIK', 'LMP', 'TISZA', 'FÜGGETLEN'
    name TEXT NOT NULL,                   -- Teljes név (pl. 'Fidesz - Magyar Polgári Szövetség')
    governing_status TEXT NOT NULL,       -- 'kormany', 'ellenzek', 'semleges'
    seats INTEGER,                        -- Frakciólétszám az alakuláskor
    color_hex TEXT,                       -- Megjelenítéshez (pl. '#FF6A00')
    FOREIGN KEY (period_id) REFERENCES period(id)
);

-- 3. KÉPVISELŐK / POLITIKUSOK
CREATE TABLE IF NOT EXISTS politician (
    id TEXT PRIMARY KEY,                   -- pl. 'orban_viktor', 'magyar_peter'
    name TEXT NOT NULL,                   -- Teljes név
    default_group_id TEXT,                -- Alapértelmezett frakciója
    title TEXT,                           -- pl. 'miniszterelnök', 'miniszter', 'képviselő', 'házelnök'
    FOREIGN KEY (default_group_id) REFERENCES parliamentary_group(id)
);

-- 4. ÜLÉSNAPOK
CREATE TABLE IF NOT EXISTS sitting_day (
    id TEXT PRIMARY KEY,                   -- pl. '2010_001', '2026_001'
    period_id TEXT NOT NULL,
    sitting_number INTEGER NOT NULL,      -- Ülésnap sorszáma
    sitting_date DATE NOT NULL,           -- Ülésnap dátuma
    session_type TEXT,                    -- 'rendes', 'rendkívüli', 'alakuló'
    source_url TEXT,                      -- Hivatalos jegyzőkönyv link
    FOREIGN KEY (period_id) REFERENCES period(id)
);

-- 5. FELSZÓLALÁS TÍPUSOK TAXONÓMIÁJA
CREATE TABLE IF NOT EXISTS speech_type (
    code TEXT PRIMARY KEY,                -- pl. 'NAPIREND_ELOTTI', 'EXPOZE', 'VEZERSZONOKI', 'FELSZOLALAS', 'KETPERCES', 'UGYRENDI', 'ZARSZO', 'AZONNALI_KERDES_SZOBELI', 'INTERPELLACIO_SZOBELI', 'KORMANYZATI_VALASZ'
    name TEXT NOT NULL,                   -- Magyar elnevezés
    description TEXT
);

-- 6. TÉMAKATEGÓRIÁK TAXONÓMIÁJA (CAP / Comparative Agendas Project adaptáció)
CREATE TABLE IF NOT EXISTS topic_category (
    code TEXT PRIMARY KEY,                -- pl. 'GAZDASAG', 'EGESZSEGUGY', 'OKTATAS', 'JOGALLAM', 'KULUGY', stb.
    name TEXT NOT NULL,                   -- Főkategória neve
    description TEXT,
    parent_code TEXT,                     -- Alkategóriák esetén a főkategória kódja
    keywords TEXT,                        -- Vesszővel elválasztott kiemelt kulcsszavak
    FOREIGN KEY (parent_code) REFERENCES topic_category(code)
);

-- 7. PARLAMENTI FELSZÓLALÁSOK (BESZÉDEK)
CREATE TABLE IF NOT EXISTS speech (
    id TEXT PRIMARY KEY,                   -- Egyedi azonosító: {period_id}_{sitting_number}_{speech_index}
    period_id TEXT NOT NULL,
    sitting_day_id TEXT NOT NULL,
    sequence_number INTEGER NOT NULL,     -- Felszólalás sorrendje az ülésnapon
    speaker_name TEXT NOT NULL,           -- Felszólaló neve (ahogy a jegyzőkönyvben szerepel)
    politician_id TEXT,                   -- Hivatkozás a politikus táblára ha normalizált
    group_id TEXT,                        -- Frakció azonosító
    speech_type_code TEXT NOT NULL,       -- Típus kód
    agenda_item TEXT,                     -- Napirendi pont címe
    bill_id TEXT,                         -- Kapcsolódó törvényjavaslat/iromány száma (pl. T/123)
    start_time TEXT,                      -- Felszólalás kezdete (pl. '10:15')
    end_time TEXT,                        -- Felszólalás vége (pl. '10:28')
    duration_seconds INTEGER,             -- Időtartam másodpercben
    word_count INTEGER,                   -- Szószám
    full_text TEXT NOT NULL,              -- Teljes jegyzőkönyvi felszólalás szöveg
    source_url TEXT,                      -- Hivatalos forrás link a felszólalásra
    FOREIGN KEY (period_id) REFERENCES period(id),
    FOREIGN KEY (sitting_day_id) REFERENCES sitting_day(id),
    FOREIGN KEY (politician_id) REFERENCES politician(id),
    FOREIGN KEY (group_id) REFERENCES parliamentary_group(id),
    FOREIGN KEY (speech_type_code) REFERENCES speech_type(code)
);

-- 8. PARLAMENTI KÉRDÉSEK ÉS INTERPELLÁCIÓK
CREATE TABLE IF NOT EXISTS question (
    id TEXT PRIMARY KEY,                   -- Egyedi iromány/kérdés azonosító (pl. '2010_K_00123')
    period_id TEXT NOT NULL,
    document_number TEXT,                 -- Hivatalos irományszám (pl. 'K/142', 'I/88', 'A/12')
    question_type TEXT NOT NULL,          -- 'interpellacio', 'azonnali_kerdes', 'szobeli_kerdes', 'irasbeli_kerdes'
    title TEXT NOT NULL,                  -- A kérdés címe/tárgya
    submitter_name TEXT NOT NULL,         -- Benyújtó képviselő neve
    submitter_group_id TEXT,              -- Benyújtó frakciója
    target_person TEXT,                   -- Címzett (pl. 'Orbán Viktor miniszterelnök')
    target_ministry TEXT,                 -- Címzett minisztérium / szerv
    submission_date DATE,                 -- Benyújtás dátuma
    answered_date DATE,                   -- Megválaszolás / elhangzás dátuma
    question_text TEXT NOT NULL,          -- Kérdés szövege
    answer_text TEXT,                     -- Kormányzati válasz szövege
    responder_name TEXT,                  -- Válaszadó személy neve
    accepted_by_submitter INTEGER,        -- Képviselő elfogadta-e a választ? (1: Igen, 0: Nem, NULL: nem releváns)
    accepted_by_parliament INTEGER,       -- Országgyűlés elfogadta-e? (1: Igen, 0: Nem, NULL: nem releváns)
    source_url TEXT,
    FOREIGN KEY (period_id) REFERENCES period(id),
    FOREIGN KEY (submitter_group_id) REFERENCES parliamentary_group(id)
);

-- 9. FELSZÓLALÁSOK TÉMABESOROLÁSA (KATEGORIZÁCIÓ)
CREATE TABLE IF NOT EXISTS speech_classification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    speech_id TEXT NOT NULL,
    primary_topic_code TEXT NOT NULL,     -- Elsődleges főkategória
    secondary_topic_code TEXT,            -- Másodlagos kategória (ha összetett téma)
    confidence REAL,                      -- AI/modell bizonyossági pontszám (0.0 - 1.0)
    summary TEXT,                         -- 1-2 mondatos tematikus összefoglaló a felszólalás lényegéről
    extracted_keywords TEXT,              -- JSON vagy vesszős lista a kinyert kulcsszavakról
    classification_method TEXT,           -- 'ai_gemini', 'keyword_rules', 'human_curated'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (speech_id) REFERENCES speech(id),
    FOREIGN KEY (primary_topic_code) REFERENCES topic_category(code),
    FOREIGN KEY (secondary_topic_code) REFERENCES topic_category(code)
);

-- 10. KÉRDÉSEK TÉMABESOROLÁSA
CREATE TABLE IF NOT EXISTS question_classification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT NOT NULL,
    primary_topic_code TEXT NOT NULL,
    secondary_topic_code TEXT,
    confidence REAL,
    summary TEXT,
    extracted_keywords TEXT,
    classification_method TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES question(id),
    FOREIGN KEY (primary_topic_code) REFERENCES topic_category(code),
    FOREIGN KEY (secondary_topic_code) REFERENCES topic_category(code)
);

-- =====================================================================
-- INDEXEK A GYORS LEKÉRDEZÉSEKHEZ ÉS ELEMZÉSEKHEZ
-- =====================================================================
CREATE INDEX IF NOT EXISTS idx_speech_period ON speech(period_id);
CREATE INDEX IF NOT EXISTS idx_speech_group ON speech(group_id);
CREATE INDEX IF NOT EXISTS idx_speech_type ON speech(speech_type_code);
CREATE INDEX IF NOT EXISTS idx_speech_sitting ON speech(sitting_day_id);
CREATE INDEX IF NOT EXISTS idx_question_period ON question(period_id);
CREATE INDEX IF NOT EXISTS idx_question_type ON question(question_type);
CREATE INDEX IF NOT EXISTS idx_question_group ON question(submitter_group_id);
CREATE INDEX IF NOT EXISTS idx_speech_class_topic ON speech_classification(primary_topic_code);
CREATE INDEX IF NOT EXISTS idx_question_class_topic ON question_classification(primary_topic_code);

-- =====================================================================
-- TELJES SZÖVEGES KERESÉS (FULL-TEXT SEARCH - FTS5)
-- Lehetővé teszi, hogy másodpercek alatt bármilyen kifejezésre, törvényre,
-- témára vagy politikus mondatára rákeressünk a több ezer felszólalás között!
-- =====================================================================
CREATE VIRTUAL TABLE IF NOT EXISTS speech_fts USING fts5(
    speaker_name,
    agenda_item,
    full_text,
    content='speech',
    content_rowid='rowid'
);

-- Triggerek az FTS tábla automatikus szinkronizálásához
CREATE TRIGGER IF NOT EXISTS speech_ai AFTER INSERT ON speech BEGIN
  INSERT INTO speech_fts(rowid, speaker_name, agenda_item, full_text)
  VALUES (new.rowid, new.speaker_name, new.agenda_item, new.full_text);
END;

CREATE TRIGGER IF NOT EXISTS speech_ad AFTER DELETE ON speech BEGIN
  INSERT INTO speech_fts(speech_fts, rowid, speaker_name, agenda_item, full_text)
  VALUES ('delete', old.rowid, old.speaker_name, old.agenda_item, old.full_text);
END;

CREATE TRIGGER IF NOT EXISTS speech_au AFTER UPDATE ON speech BEGIN
  INSERT INTO speech_fts(speech_fts, rowid, speaker_name, agenda_item, full_text)
  VALUES ('delete', old.rowid, old.speaker_name, old.agenda_item, old.full_text);
  INSERT INTO speech_fts(rowid, speaker_name, agenda_item, full_text)
  VALUES (new.rowid, new.speaker_name, new.agenda_item, new.full_text);
END;

-- 11. MÚLTRA VALÓ REFLEXIÓ ÉS AZ ELŐZŐ KORSZAK BÍRÁLATA (RETROSPECTIVE CRITIQUE / BLAME)
-- Kifejezetten a kormánypárti képviselők diskurzusának elemzésére: hányszor és hogyan
-- utaltak vissza a korábbi kormányzati időszakra rosszként (pl. "elmúlt 8 év", "elmúlt 16 év", "örökölt romhalmaz", "üres kassza")
CREATE TABLE IF NOT EXISTS speech_retrospective_critique (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    speech_id TEXT NOT NULL UNIQUE,
    has_past_critique INTEGER NOT NULL DEFAULT 0, -- 1: Igen, volt negatív reflexió a múltra, 0: Nem volt
    target_era TEXT,                             -- pl. '2002-2010 (MSZP-SZDSZ)', '2010-2026 (NER/Fidesz)', 'altalanos_elodek'
    critique_intensity REAL DEFAULT 0.0,         -- 0.0 - 1.0 intenzitási fokozat
    mention_count INTEGER DEFAULT 0,             -- Hány különálló fordulatban/mondatban utalt a múltra
    matched_patterns TEXT,                       -- JSON lista a felismert kifejezésekről
    excerpts TEXT,                               -- A konkrét idézetek / mondatrészletek a beszédből
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (speech_id) REFERENCES speech(id)
);

CREATE INDEX IF NOT EXISTS idx_critique_has_past ON speech_retrospective_critique(has_past_critique);

-- =====================================================================
-- KÉNYELMES ANALITIKAI NÉZETEK (VIEWS)
-- =====================================================================

-- Felszólalások összefoglaló nézete frakció, téma és múltbírálati szűrő szerint
DROP VIEW IF EXISTS v_speeches_categorized;
CREATE VIEW v_speeches_categorized AS
SELECT 
    s.id AS speech_id,
    s.period_id,
    p.name AS period_name,
    sd.sitting_date,
    sd.sitting_number,
    s.speaker_name,
    pg.name AS group_name,
    pg.governing_status,
    st.name AS speech_type_name,
    s.agenda_item,
    s.word_count,
    tc.name AS primary_topic,
    sc.confidence,
    sc.summary,
    COALESCE(src.has_past_critique, 0) AS has_past_critique,
    src.target_era,
    src.critique_intensity,
    COALESCE(src.mention_count, 0) AS past_critique_mentions,
    src.matched_patterns AS past_critique_patterns,
    src.excerpts AS past_critique_excerpts,
    s.source_url
FROM speech s
JOIN period p ON s.period_id = p.id
JOIN sitting_day sd ON s.sitting_day_id = sd.id
LEFT JOIN parliamentary_group pg ON s.group_id = pg.id
JOIN speech_type st ON s.speech_type_code = st.code
LEFT JOIN speech_classification sc ON s.id = sc.speech_id
LEFT JOIN topic_category tc ON sc.primary_topic_code = tc.code
LEFT JOIN speech_retrospective_critique src ON s.id = src.speech_id;

-- Kérdések összefoglaló nézete
CREATE VIEW IF NOT EXISTS v_questions_categorized AS
SELECT 
    q.id AS question_id,
    q.period_id,
    p.name AS period_name,
    q.document_number,
    q.question_type,
    q.title,
    q.submitter_name,
    pg.name AS submitter_group_name,
    pg.governing_status,
    q.target_person,
    q.target_ministry,
    q.submission_date,
    q.answered_date,
    tc.name AS primary_topic,
    qc.confidence,
    qc.summary,
    q.accepted_by_submitter,
    q.source_url
FROM question q
JOIN period p ON q.period_id = p.id
LEFT JOIN parliamentary_group pg ON q.submitter_group_id = pg.id
LEFT JOIN question_classification qc ON q.id = qc.question_id
LEFT JOIN topic_category tc ON qc.primary_topic_code = tc.code;

-- =====================================================================
-- 12. TÖRVÉNYJAVASLATOK ÉS JOGALKOTÁS (BILLS / PROPOSALS)
-- =====================================================================
CREATE TABLE IF NOT EXISTS bill (
    id TEXT PRIMARY KEY,                       -- pl. '2010_T_29', '2026_T_7'
    period_id TEXT NOT NULL,                  -- '2010' vagy '2026'
    bill_number TEXT NOT NULL,                -- 'T/29', 'T/7', stb.
    title TEXT NOT NULL,                      -- Teljes törvényjavaslat cím
    short_title TEXT,                         -- Rövidített, közérthető elnevezés
    affected_law TEXT,                        -- Módosított vagy megalkotott törvény megnevezése (pl. '1993. évi LV. tv. (Állampolgárság)' vagy 'Új önálló törvény')
    bill_type TEXT,                           -- 'onallo' (új törvény) vagy 'modosito' (törvénymódosítás)
    submitter_names TEXT,                     -- Vesszővel elválasztott benyújtó képviselők / előterjesztők
    submitter_group_id TEXT,                  -- '2010_FIDESZ', '2026_TISZA', '2026_KORMANY', stb.
    submitter_party TEXT,                     -- Frakció / előterjesztő kódja (pl. 'FIDESZ', 'TISZA', 'KORMANY', 'MI_HAZANK', 'KDNP', 'MSZP', 'LMP')
    governing_status TEXT,                    -- 'kormany', 'ellenzek', 'semleges'
    submission_date DATE,                     -- Benyújtás dátuma
    decision_date DATE,                       -- Döntés / elfogadás / elutasítás dátuma
    status TEXT NOT NULL,                     -- 'elfogadva', 'elutasitva', 'folyamatban'
    is_enacted INTEGER NOT NULL DEFAULT 0,    -- 1: Elfogadva (törvény lett), 0: Nem elfogadva (elutasítva / folyamatban)
    yes_votes INTEGER DEFAULT 0,              -- Igen szavazatok
    no_votes INTEGER DEFAULT 0,               -- Nem szavazatok
    abstain_votes INTEGER DEFAULT 0,          -- Tartózkodások
    vote_count INTEGER DEFAULT 0,             -- Hány szavazás kapcsolódott hozzá (módosítók + záró)
    primary_topic_code TEXT,                  -- CAP téma kód (pl. 'NEMZETPOLITIKA')
    secondary_topic_code TEXT,                -- Másodlagos téma kód
    topic_summary TEXT,                       -- Tematikus lényeg
    source_url TEXT,                          -- WebAPI vagy parlament.hu link
    FOREIGN KEY (period_id) REFERENCES period(id),
    FOREIGN KEY (primary_topic_code) REFERENCES topic_category(code)
);

CREATE INDEX IF NOT EXISTS idx_bill_period ON bill(period_id);
CREATE INDEX IF NOT EXISTS idx_bill_party ON bill(submitter_party);
CREATE INDEX IF NOT EXISTS idx_bill_enacted ON bill(is_enacted);
CREATE INDEX IF NOT EXISTS idx_bill_topic ON bill(primary_topic_code);

-- Törvényjavaslatok összefoglaló nézete
DROP VIEW IF EXISTS v_bills_categorized;
CREATE VIEW v_bills_categorized AS
SELECT 
    b.id AS bill_id,
    b.period_id,
    p.name AS period_name,
    b.bill_number,
    b.title,
    b.short_title,
    b.affected_law,
    b.bill_type,
    b.submitter_names,
    b.submitter_party,
    b.governing_status,
    b.submission_date,
    b.decision_date,
    b.status,
    b.is_enacted,
    b.yes_votes,
    b.no_votes,
    b.abstain_votes,
    b.vote_count,
    tc.name AS primary_topic,
    b.topic_summary,
    b.source_url
FROM bill b
JOIN period p ON b.period_id = p.id
LEFT JOIN topic_category tc ON b.primary_topic_code = tc.code;

