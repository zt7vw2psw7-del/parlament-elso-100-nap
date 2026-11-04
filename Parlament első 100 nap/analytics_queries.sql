-- =====================================================================
-- ELEMZÉSI LEKÉRDEZÉSEK: 2010 VS 2026 ELSŐ 100 NAPJÁNAK ÖSSZEHASONLÍTÁSA
-- =====================================================================

-- 1. TÉMÁK MEGOSZLÁSA KORSZAKONKÉNT (Miről szólt az első 100 nap?)
SELECT 
    p.name AS korszak,
    tc.name AS fo_tema,
    COUNT(s.id) AS felszolalasok_szama,
    ROUND(SUM(s.word_count) / 1000.0, 1) AS osszes_ezer_szo,
    ROUND(AVG(sc.confidence), 2) AS atlagos_ai_bizonyossag
FROM speech s
JOIN period p ON s.period_id = p.id
JOIN speech_classification sc ON s.id = sc.speech_id
JOIN topic_category tc ON sc.primary_topic_code = tc.code
GROUP BY p.name, tc.name
ORDER BY p.id ASC, felszolalasok_szama DESC;

-- 2. KORMÁNYPÁRT VS. ELLENZÉK AKTIVITÁSA (Frakciók szerint)
SELECT 
    p.id AS ev,
    pg.name AS frakcio,
    pg.governing_status AS statusz,
    COUNT(s.id) AS felszolalasok,
    SUM(s.duration_seconds) / 60 AS osszes_beszedido_perc,
    SUM(s.word_count) AS osszes_szo,
    ROUND(AVG(s.word_count), 0) AS atlagos_felszolalas_hossz_szo
FROM speech s
JOIN period p ON s.period_id = p.id
JOIN parliamentary_group pg ON s.group_id = pg.id
GROUP BY p.id, pg.name, pg.governing_status
ORDER BY p.id ASC, osszes_szo DESC;

-- 3. FELSZÓLALÁS TÍPUSOK ARÁNYA A KÉT IDŐSZAKBAN
SELECT 
    s.period_id AS korszak,
    st.name AS felszolalas_tipus,
    COUNT(*) AS darabszam,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY s.period_id), 1) AS arany_szazalek
FROM speech s
JOIN speech_type st ON s.speech_type_code = st.code
GROUP BY s.period_id, st.name
ORDER BY s.period_id, darabszam DESC;

-- 4. KÉRDÉSEK ÉS INTERPELLÁCIÓK TÉMÁI ÉS ELFOGADÁSI ARÁNYA
SELECT 
    q.period_id AS korszak,
    tc.name AS tema,
    COUNT(q.id) AS kerdesek_szama,
    SUM(CASE WHEN q.question_type = 'interpellacio' THEN 1 ELSE 0 END) AS interpellaciok,
    SUM(CASE WHEN q.question_type = 'azonnali_kerdes' THEN 1 ELSE 0 END) AS azonnali_kerdesek,
    ROUND(100.0 * SUM(CASE WHEN q.accepted_by_submitter = 1 THEN 1 ELSE 0 END) / COUNT(q.id), 1) AS kepviselo_altal_elfogadva_szazalek
FROM question q
JOIN question_classification qc ON q.id = qc.question_id
JOIN topic_category tc ON qc.primary_topic_code = tc.code
GROUP BY q.period_id, tc.name
ORDER BY q.period_id, kerdesek_szama DESC;

-- 5. A LEGTÖBBET BESZÉLŐ POLITIKUSOK TOPLISTÁJA
SELECT 
    s.period_id AS korszak,
    s.speaker_name AS kepviselo,
    pg.code AS frakcio,
    COUNT(s.id) AS felszolalasok_szama,
    SUM(s.word_count) AS osszes_szoszam,
    SUM(s.duration_seconds) / 60 AS osszes_perc
FROM speech s
LEFT JOIN parliamentary_group pg ON s.group_id = pg.id
GROUP BY s.period_id, s.speaker_name, pg.code
ORDER BY s.period_id ASC, osszes_szoszam DESC;

-- 6. FULL-TEXT SEARCH (Kifejezések előfordulása kontextussal)
-- Példa: Keresés az 'adó', 'egészségügy', 'korrupció' vagy 'szuverenitás' kifejezésekre
SELECT 
    s.period_id AS ev,
    s.speaker_name,
    s.agenda_item,
    snippet(speech_fts, 2, '【', '】', '...', 15) AS talalat_szovegreszlet
FROM speech_fts
JOIN speech s ON speech_fts.rowid = s.rowid
WHERE speech_fts MATCH 'jogállam* OR egészségügy* OR bankadó*'
ORDER BY s.period_id;

-- =====================================================================
-- KORMÁNYPÁRTI KÉPVISELŐK MÚLTBÍRÁLATÁNAK SZŰRÉSE ÉS ELEMZÉSE
-- ("Elmúlt 8 év" és "Elmúlt 16 év" reflexiók vizsgálata)
-- =====================================================================

-- 7. KORMÁNYPÁRTI KÉPVISELŐK MÚLTBÍRÁLATÁNAK ARÁNYA (2010 VS 2026)
-- Hányszor és mekkora arányban hivatkoztak vissza az előző kormányzatok bűneire/hibáira?
SELECT 
    p.name AS korszak,
    pg.name AS kormanyparti_frakcio,
    COUNT(s.id) AS osszes_kormanyparti_felszolalas,
    SUM(CASE WHEN v.has_past_critique = 1 THEN 1 ELSE 0 END) AS multat_biralok_szama,
    ROUND(100.0 * SUM(CASE WHEN v.has_past_critique = 1 THEN 1 ELSE 0 END) / COUNT(s.id), 1) AS multbiralati_arany_szazalek,
    SUM(v.past_critique_mentions) AS osszes_multbiralati_emlites
FROM v_speeches_categorized v
JOIN speech s ON v.speech_id = s.id
JOIN period p ON v.period_id = p.id
JOIN parliamentary_group pg ON s.group_id = pg.id
WHERE v.governing_status = 'kormany'
GROUP BY p.name, pg.name
ORDER BY p.id;

-- 8. KIK BESZÉLTEK A LEGTÖBBET A RÉGI IDŐKRŐL ROSSZKÉNT?
SELECT 
    v.period_id AS korszak,
    v.speaker_name AS kepviselo,
    v.group_name AS frakcio,
    COUNT(*) AS osszes_beszed,
    SUM(CASE WHEN v.has_past_critique = 1 THEN 1 ELSE 0 END) AS multat_biralo_beszedek,
    SUM(v.past_critique_mentions) AS emlitett_mondatok_szama,
    ROUND(AVG(v.critique_intensity), 2) AS atlagos_intenzitas
FROM v_speeches_categorized v
WHERE v.governing_status = 'kormany' AND v.has_past_critique = 1
GROUP BY v.period_id, v.speaker_name, v.group_name
ORDER BY v.period_id, emlitett_mondatok_szama DESC;

-- 9. MELY TÉMÁKBAN JÖTT ELŐ LEGGYAKRABBAN A KORÁBBI KORSZAK BÍRÁLATA?
SELECT 
    v.period_id AS korszak,
    v.primary_topic AS tema,
    COUNT(*) AS temahoz_tartozo_kormanyparti_beszedek,
    SUM(CASE WHEN v.has_past_critique = 1 THEN 1 ELSE 0 END) AS ebbol_multat_biralo,
    ROUND(100.0 * SUM(CASE WHEN v.has_past_critique = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS multbiralati_arany_szazalek
FROM v_speeches_categorized v
WHERE v.governing_status = 'kormany'
GROUP BY v.period_id, v.primary_topic
ORDER BY v.period_id, ebbol_multat_biralo DESC;

-- 10. KONKRÉT IDÉZETEK: KORMÁNYPÁRTI KÉPVISELŐK MONDATAI A RÉGI IDŐKRŐL
SELECT 
    v.period_id AS korszak,
    v.speaker_name AS kepviselo,
    v.agenda_item AS napirendi_pont,
    v.target_era AS megjelolt_korszak,
    v.past_critique_patterns AS kulcskifejezesek,
    v.past_critique_excerpts AS idezet_a_beszedbol
FROM v_speeches_categorized v
WHERE v.governing_status = 'kormany' AND v.has_past_critique = 1
ORDER BY v.period_id, v.critique_intensity DESC;

-- =====================================================================
-- TÖRVÉNYJAVASLATOK ÉS JOGALKOTÁS ELEMZÉSE (2010 VS 2026 ELSŐ 100 NAP)
-- =====================================================================

-- 11. TÖRVÉNYJAVASLATOK ÉS JOGALKOTÁSI EREDMÉNYEK ÖSSZEFOGLALÁSA
SELECT 
    p.name AS korszak,
    COUNT(b.id) AS osszes_benyujtott_javaslat,
    SUM(b.is_enacted) AS elfogadott_torvenyek,
    SUM(CASE WHEN b.status = 'elutasitva' THEN 1 ELSE 0 END) AS elutasitott_javaslatok,
    SUM(CASE WHEN b.status = 'folyamatban' THEN 1 ELSE 0 END) AS folyamatban_maradt_javaslatok,
    ROUND(100.0 * SUM(b.is_enacted) / COUNT(b.id), 1) AS elfogadasi_arany_szazalek,
    SUM(b.vote_count) AS osszes_szavazasi_esemeny
FROM bill b
JOIN period p ON b.period_id = p.id
GROUP BY p.name;

-- 12. TÖRVÉNYJAVASLATOK BENYÚJTÓI FRAKCIÓNKÉNT (Kik hányat nyújtottak be és mi ment át?)
SELECT 
    b.period_id AS korszak,
    b.submitter_party AS frakcio,
    b.governing_status AS kormanyzati_statusz,
    COUNT(b.id) AS benyujtott_javaslatok,
    SUM(b.is_enacted) AS elfogadott_torvenyek,
    SUM(CASE WHEN b.status = 'elutasitva' THEN 1 ELSE 0 END) AS elutasitott_javaslatok,
    SUM(CASE WHEN b.status = 'folyamatban' THEN 1 ELSE 0 END) AS folyamatban_levo,
    ROUND(100.0 * SUM(b.is_enacted) / COUNT(b.id), 1) AS sikerességi_arany_szazalek
FROM bill b
GROUP BY b.period_id, b.submitter_party, b.governing_status
ORDER BY b.period_id, benyujtott_javaslatok DESC;

-- 13. TÖRVÉNYJAVASLATOK SZAKPOLITIKAI TÉMÁK (CAP) SZERINT
SELECT 
    b.period_id AS korszak,
    tc.name AS szakpolitikai_tema,
    COUNT(b.id) AS benyujtott_javaslatok,
    SUM(b.is_enacted) AS elfogadva,
    SUM(CASE WHEN b.is_enacted = 0 THEN 1 ELSE 0 END) AS nem_lett_elfogadva,
    ROUND(100.0 * SUM(b.is_enacted) / COUNT(b.id), 1) AS elfogadasi_arany_szazalek
FROM bill b
JOIN topic_category tc ON b.primary_topic_code = tc.code
GROUP BY b.period_id, tc.name
ORDER BY b.period_id, benyujtott_javaslatok DESC;

-- 14. ÉRINTETT ÉS MÓDOSÍTOTT TÖRVÉNYEK SZERINTI BONTÁS
SELECT 
    b.period_id AS korszak,
    b.affected_law AS erintett_vagy_modositott_torveny,
    b.bill_type AS tipus,
    COUNT(b.id) AS javaslatok_szama,
    SUM(b.is_enacted) AS ebbol_elfogadva
FROM bill b
GROUP BY b.period_id, b.affected_law, b.bill_type
ORDER BY b.period_id, javaslatok_szama DESC;

-- 15. A LEGFONTOSABB ELFOGADOTT ÉS ELUTASÍTOTT TÖRVÉNYJAVASLATOK RÉSZLETEI
SELECT 
    b.period_id AS korszak,
    b.bill_number AS iromany,
    b.short_title AS rovid_cim,
    b.submitter_party AS benyujto,
    b.status AS dontes,
    b.is_enacted AS elfogadva,
    b.yes_votes AS igen,
    b.no_votes AS nem,
    b.abstain_votes AS tart,
    tc.code AS cap_kod,
    tc.name AS tema,
    b.subtopic_code AS cap_altema_kod,
    b.decision_date AS dontes_datum
FROM bill b
JOIN topic_category tc ON b.primary_topic_code = tc.code
ORDER BY b.period_id, b.is_enacted DESC, b.yes_votes DESC;

-- 16. COMPARATIVE AGENDAS PROJECT (CAP) MASTER TAXONÓMIA ÖSSZESÍTÉSE
-- A 21 hivatalos főtéma megoszlása a törvényjavaslatok, beszédek és kérdések tükrében
SELECT 
    tc.code AS cap_kod,
    tc.name AS cap_tema_magyar,
    tc.name_en AS cap_tema_angol,
    SUM(CASE WHEN b.period_id = '2010' THEN 1 ELSE 0 END) AS javaslatok_2010,
    SUM(CASE WHEN b.period_id = '2026' THEN 1 ELSE 0 END) AS javaslatok_2026,
    COUNT(b.id) AS osszes_javaslat
FROM topic_category tc
LEFT JOIN bill b ON tc.code = b.primary_topic_code
WHERE tc.parent_code IS NULL
GROUP BY tc.code, tc.name, tc.name_en
ORDER BY CAST(tc.code AS INTEGER) ASC;

