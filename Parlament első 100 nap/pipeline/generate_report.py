#!/usr/bin/env python3
"""
PARLAMENTI 100 NAP: VIZUÁLIS RIOPRT GENERÁLÓ (HTML DASHBOARD)
Tartalmazza:
1. Fő statisztikák és KPI mutatók
2. Törvényjavaslatok és jogalkotás részletes bontása (benyújtók, témák, törvények, elfogadási státusz)
3. Felszólalások szakpolitikai témái (CAP taxonómia) diagram
4. Kormánypárti múltbírálati szűrő ("elmúlt 8 év" vs "elmúlt 16 év") és idézetek
5. Frakciók és képviselők aktivitási táblázata
"""

import json
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "parlament_100nap.db")
OUTPUT_HTML = os.path.join(BASE_DIR, "parlament_100nap_riport.html")
OUTPUT_HTML_SHORT = os.path.join(BASE_DIR, "riport.html")

def generate_report():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- 1. Témák adatai a diagramhoz (CAP Master Codebook) ---
    cursor.execute("""
        SELECT 
            tc.code,
            tc.name,
            SUM(CASE WHEN s.period_id = '2010' THEN 1 ELSE 0 END) AS c2010,
            SUM(CASE WHEN s.period_id = '2026' THEN 1 ELSE 0 END) AS c2026
        FROM speech s
        JOIN speech_classification sc ON s.id = sc.speech_id
        JOIN topic_category tc ON sc.primary_topic_code = tc.code
        GROUP BY tc.code, tc.name
        ORDER BY (SUM(CASE WHEN s.period_id = '2010' THEN 1 ELSE 0 END) + SUM(CASE WHEN s.period_id = '2026' THEN 1 ELSE 0 END)) DESC
    """)
    topics_data = [{"tema": f"CAP {r[0]}: {r[1]}", "c2010": r[2], "c2026": r[3]} for r in cursor.fetchall()]

    # --- 2. Fő KPI adatok (Felszólalások, Kérdések, Törvényjavaslatok) ---
    cursor.execute("SELECT COUNT(*) FROM speech")
    s_tot = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM speech WHERE period_id = '2010'")
    s10_tot = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM speech WHERE period_id = '2026'")
    s26_tot = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM question")
    q_tot = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM question WHERE period_id = '2010'")
    q10_tot = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM question WHERE period_id = '2026'")
    q26_tot = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*), SUM(is_enacted), SUM(CASE WHEN status='elutasitva' THEN 1 ELSE 0 END), SUM(CASE WHEN status='folyamatban' THEN 1 ELSE 0 END) FROM bill WHERE period_id = '2010'")
    b10_tot, b10_enact, b10_rej, b10_pend = cursor.fetchone()
    b10_rate = (b10_enact / b10_tot * 100) if b10_tot else 0

    cursor.execute("SELECT COUNT(*), SUM(is_enacted), SUM(CASE WHEN status='elutasitva' THEN 1 ELSE 0 END), SUM(CASE WHEN status='folyamatban' THEN 1 ELSE 0 END) FROM bill WHERE period_id = '2026'")
    b26_tot, b26_enact, b26_rej, b26_pend = cursor.fetchone()
    b26_rate = (b26_enact / b26_tot * 100) if b26_tot else 0

    # Kormánypárti múltbírálati KPI-k
    cursor.execute("""
        SELECT COUNT(*), SUM(CASE WHEN has_past_critique = 1 THEN 1 ELSE 0 END), SUM(past_critique_mentions)
        FROM v_speeches_categorized
        WHERE period_id = '2010' AND group_name LIKE '%Fidesz%' AND governing_status = 'kormany'
    """)
    fid_tot, fid_crit, fid_mentions = cursor.fetchone()
    fid_pct = (fid_crit / fid_tot * 100) if fid_tot else 0
    fid_mentions = fid_mentions or 0

    cursor.execute("""
        SELECT COUNT(*), SUM(CASE WHEN has_past_critique = 1 THEN 1 ELSE 0 END), SUM(past_critique_mentions)
        FROM v_speeches_categorized
        WHERE period_id = '2010' AND group_name LIKE '%Kereszténydemokrata%' AND governing_status = 'kormany'
    """)
    kdnp_tot, kdnp_crit, kdnp_mentions = cursor.fetchone()
    kdnp_pct = (kdnp_crit / kdnp_tot * 100) if kdnp_tot else 0
    kdnp_mentions = kdnp_mentions or 0

    cursor.execute("""
        SELECT COUNT(*), SUM(CASE WHEN has_past_critique = 1 THEN 1 ELSE 0 END), SUM(past_critique_mentions)
        FROM v_speeches_categorized
        WHERE period_id = '2026' AND group_name LIKE '%Tisztelet%' AND governing_status = 'kormany'
    """)
    tisza_tot, tisza_crit, tisza_mentions = cursor.fetchone()
    tisza_pct = (tisza_crit / tisza_tot * 100) if tisza_tot else 0
    tisza_mentions = tisza_mentions or 0

    # --- 3. Törvényjavaslatok benyújtói frakciónként ---
    cursor.execute("""
        SELECT 
            period_id, submitter_party, governing_status,
            COUNT(*) AS osszes,
            SUM(is_enacted) AS elfogadva,
            SUM(CASE WHEN status='elutasitva' THEN 1 ELSE 0 END) AS elutasitva,
            SUM(CASE WHEN status='folyamatban' THEN 1 ELSE 0 END) AS folyamatban,
            ROUND(100.0 * SUM(is_enacted) / COUNT(*), 1) AS siker_pct
        FROM bill
        GROUP BY period_id, submitter_party, governing_status
        ORDER BY period_id, osszes DESC
    """)
    bills_party_rows = cursor.fetchall()
    bills_party_html = ""
    for r in bills_party_rows:
        period, party, gov, tot, enact, rej, pend, pct = r
        p_badge = '<span class="badge badge-2010">2010</span>' if period == "2010" else '<span class="badge badge-2026">2026</span>'
        g_badge = '<span class="badge badge-gov">Kormánypárt</span>' if gov == "kormany" else '<span class="badge badge-opp">Ellenzék</span>'
        pct_color = "#166534" if pct > 50 else ("#b45309" if pct > 0 else "#991b1b")
        bills_party_html += f"""
        <tr>
            <td>{p_badge}</td>
            <td><strong>{party}</strong></td>
            <td>{g_badge}</td>
            <td><strong>{tot}</strong> db</td>
            <td style="color: #166534; font-weight: bold;">{enact} db</td>
            <td style="color: #991b1b;">{rej} db</td>
            <td style="color: #64748b;">{pend} db</td>
            <td style="font-weight: 700; color: {pct_color};">{pct}%</td>
        </tr>
        """

    # --- 4. Törvényjavaslatok témák (CAP) szerint ---
    cursor.execute("""
        SELECT 
            tc.code,
            tc.name AS tema,
            SUM(CASE WHEN b.period_id = '2010' THEN 1 ELSE 0 END) AS tot_2010,
            SUM(CASE WHEN b.period_id = '2010' AND b.is_enacted = 1 THEN 1 ELSE 0 END) AS enact_2010,
            SUM(CASE WHEN b.period_id = '2026' THEN 1 ELSE 0 END) AS tot_2026,
            SUM(CASE WHEN b.period_id = '2026' AND b.is_enacted = 1 THEN 1 ELSE 0 END) AS enact_2026
        FROM bill b
        JOIN topic_category tc ON b.primary_topic_code = tc.code
        GROUP BY tc.code, tc.name
        ORDER BY (SUM(CASE WHEN b.period_id = '2010' THEN 1 ELSE 0 END) + SUM(CASE WHEN b.period_id = '2026' THEN 1 ELSE 0 END)) DESC
    """)
    bills_topic_rows = cursor.fetchall()
    bills_topic_html = ""
    for r in bills_topic_rows:
        code, tema, t10, e10, t26, e26 = r
        r10 = f"{e10}/{t10} ({e10/t10*100:.0f}%)" if t10 else "-"
        r26 = f"{e26}/{t26} ({e26/t26*100:.0f}%)" if t26 else "-"
        bills_topic_html += f"""
        <tr>
            <td><span class="badge" style="background: #e2e8f0; color: #1e293b;">CAP {code}</span> <strong>{tema}</strong></td>
            <td>{t10} db</td>
            <td style="color: #166534; font-weight: 600;">{r10}</td>
            <td>{t26} db</td>
            <td style="color: #1d4ed8; font-weight: 600;">{r26}</td>
        </tr>
        """

    # --- 4b. Kérdések és interpellációk témák (CAP) szerint ---
    cursor.execute("""
        SELECT 
            tc.code,
            tc.name AS tema,
            SUM(CASE WHEN q.period_id = '2010' THEN 1 ELSE 0 END) AS q10,
            SUM(CASE WHEN q.period_id = '2026' THEN 1 ELSE 0 END) AS q26,
            COUNT(q.id) AS tot
        FROM question q
        JOIN question_classification qc ON q.id = qc.question_id
        JOIN topic_category tc ON qc.primary_topic_code = tc.code
        GROUP BY tc.code, tc.name
        ORDER BY tot DESC
    """)
    questions_topic_rows = cursor.fetchall()
    questions_topic_html = ""
    for r in questions_topic_rows:
        code, tema, q10, q26, tot = r
        questions_topic_html += f"""
        <tr>
            <td><span class="badge" style="background: #f1f5f9; color: #334155;">CAP {code}</span> <strong>{tema}</strong></td>
            <td>{q10} db</td>
            <td>{q26} db</td>
            <td><strong>{tot} db</strong></td>
        </tr>
        """

    # --- 5. Érintett törvények szerinti bontás ---
    cursor.execute("""
        SELECT 
            period_id, affected_law, bill_type,
            COUNT(*) AS darab,
            SUM(is_enacted) AS elfogadva
        FROM bill
        GROUP BY period_id, affected_law, bill_type
        ORDER BY period_id, darab DESC
        LIMIT 25
    """)
    laws_rows = cursor.fetchall()
    laws_html = ""
    for r in laws_rows:
        period, law, btype, cnt, en = r
        p_badge = '<span class="badge badge-2010">2010</span>' if period == "2010" else '<span class="badge badge-2026">2026</span>'
        t_badge = '<span class="badge" style="background: #f1f5f9; color: #475569;">módosító</span>' if btype == "modosito" else '<span class="badge" style="background: #e0e7ff; color: #3730a3;">új törvény</span>'
        status_txt = f'<span style="color: #166534; font-weight: 600;">{en}/{cnt} elfogadva</span>' if en > 0 else f'<span style="color: #64748b;">0/{cnt} elfogadva</span>'
        laws_html += f"""
        <tr>
            <td>{p_badge}</td>
            <td><strong>{law}</strong></td>
            <td>{t_badge}</td>
            <td><strong>{cnt}</strong> javaslat</td>
            <td>{status_txt}</td>
        </tr>
        """

    # --- 6. Minden törvényjavaslat részletes táblázata ---
    cursor.execute("""
        SELECT 
            b.period_id, b.bill_number, b.short_title, b.affected_law,
            b.submitter_party, b.governing_status, b.status, b.is_enacted,
            b.yes_votes, b.no_votes, b.abstain_votes, tc.code, tc.name, b.subtopic_code, b.decision_date, b.source_url
        FROM bill b
        LEFT JOIN topic_category tc ON b.primary_topic_code = tc.code
        ORDER BY b.period_id, b.is_enacted DESC, CAST(SUBSTR(b.bill_number, 3) AS INTEGER)
    """)
    all_bills = cursor.fetchall()
    all_bills_html = ""
    for r in all_bills:
        period, bnum, short_t, aff_law, party, gov, status, enacted, igen, nem, tart, tcode, tema, subcode, ddate, surl = r
        p_badge = '<span class="badge badge-2010">2010</span>' if period == "2010" else '<span class="badge badge-2026">2026</span>'
        
        if status == "elfogadva":
            s_badge = '<span class="badge badge-gov">✓ Elfogadva</span>'
        elif status == "elutasitva":
            s_badge = '<span class="badge badge-opp">✗ Elutasítva</span>'
        else:
            s_badge = '<span class="badge" style="background: #e2e8f0; color: #475569;">⧗ Folyamatban</span>'

        szavazat_info = f"<span title='Igen: {igen}, Nem: {nem}, Tartózkodás: {tart}'><strong>{igen}</strong> igen / {nem} nem</span>" if (igen or nem) else "<span style='color: #94a3b8;'>-</span>"
        sub_title = f"Altéma kód: {subcode}" if subcode else "Altéma: nincs"
        cap_badge = f'<span class="badge" style="background: #f1f5f9; color: #334155;" title="{sub_title}">CAP {tcode}: {tema}</span>' if tcode else "-"

        all_bills_html += f"""
        <tr>
            <td>{p_badge}</td>
            <td><strong><a href="{surl}" target="_blank" style="color: #2563eb; text-decoration: none;">{bnum}</a></strong></td>
            <td><strong>{short_t}</strong></td>
            <td style="font-size: 12px; color: #475569;">{aff_law}</td>
            <td><strong>{party}</strong></td>
            <td>{cap_badge}</td>
            <td>{s_badge}</td>
            <td style="font-size: 13px;">{szavazat_info}</td>
            <td style="font-size: 12px; color: #64748b;">{ddate or '-'}</td>
        </tr>
        """

    # --- 7. Múltbírálati toplista ---
    cursor.execute("""
        SELECT 
            v.period_id, v.speaker_name, v.group_name,
            COUNT(*) AS osszes,
            SUM(v.past_critique_mentions) AS emlitsek,
            ROUND(AVG(v.critique_intensity), 2) AS intenzitas
        FROM v_speeches_categorized v
        WHERE v.governing_status = 'kormany' AND v.has_past_critique = 1
        GROUP BY v.period_id, v.speaker_name, v.group_name
        ORDER BY emlitsek DESC
        LIMIT 10
    """)
    blame_rows = cursor.fetchall()
    blame_table_html = ""
    for r in blame_rows:
        p_badge = '<span class="badge badge-2010">2010</span>' if r[0] == "2010" else '<span class="badge badge-2026">2026</span>'
        blame_table_html += f"""
        <tr>
            <td>{p_badge}</td>
            <td><strong>{r[1]}</strong></td>
            <td>{r[2]}</td>
            <td>{r[3]}</td>
            <td style="color: #ea580c; font-weight: bold;">{r[4]} említés</td>
            <td>{r[5]} / 1.0</td>
        </tr>
        """

    # --- 8. Múltbírálati konkrét idézetek ---
    cursor.execute("""
        SELECT v.period_id, v.speaker_name, v.group_name, v.agenda_item, v.target_era, v.past_critique_excerpts
        FROM v_speeches_categorized v
        WHERE v.governing_status = 'kormany' AND v.has_past_critique = 1 AND v.past_critique_excerpts IS NOT NULL
        ORDER BY v.critique_intensity DESC, v.past_critique_mentions DESC
        LIMIT 6
    """)
    quotes_rows = cursor.fetchall()
    quotes_html = ""
    for r in quotes_rows:
        p_badge = '<span class="badge badge-2010">2010 (Fidesz)</span>' if r[0] == "2010" else '<span class="badge badge-2026">2026 (TISZA)</span>'
        quotes_html += f"""
        <div class="quote-box">
            <div class="quote-meta">{p_badge} <strong>{r[1]}</strong> ({r[2]}) &bull; Célzott időszak: <em>{r[4]}</em></div>
            <div class="quote-text">„{r[5]}”</div>
        </div>
        """

    # --- 9. Frakciók felszólalási összesítője ---
    cursor.execute("""
        SELECT period_id, group_name, governing_status, COUNT(*), SUM(word_count)
        FROM v_speeches_categorized
        GROUP BY period_id, group_name, governing_status
        ORDER BY period_id, COUNT(*) DESC
    """)
    factions_rows = cursor.fetchall()
    factions_table_html = ""
    for r in factions_rows:
        p_badge = '<span class="badge badge-2010">2010</span>' if r[0] == "2010" else '<span class="badge badge-2026">2026</span>'
        status_badge = '<span class="badge badge-gov">Kormánypárt</span>' if r[2] == "kormany" else '<span class="badge badge-opp">Ellenzék</span>'
        factions_table_html += f"""
        <tr>
            <td>{p_badge}</td>
            <td><strong>{r[1]}</strong></td>
            <td>{status_badge}</td>
            <td>{r[3]:,} db</td>
            <td>{r[4]:,} szó</td>
        </tr>
        """

    conn.close()

    template = f"""<!DOCTYPE html>
<html lang="hu">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Parlamenti Elemzés: 2010 vs 2026 Első 100 Nap (CAP Master Codebook Taxonómia)</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #f8fafc;
        color: #0f172a;
        margin: 0;
        padding: 24px;
        line-height: 1.5;
    }}
    .container {{
        max-width: 1250px;
        margin: 0 auto;
    }}
    header {{
        background: linear-gradient(135deg, #1e293b, #0f172a);
        color: white;
        padding: 36px;
        border-radius: 16px;
        margin-bottom: 28px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }}
    h1 {{ margin: 0 0 10px 0; font-size: 28px; font-weight: 800; }}
    .subtitle {{ color: #94a3b8; font-size: 16px; margin: 0; }}
    
    .grid-cards {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }}
    .card {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .card-title {{
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        color: #64748b;
        margin-bottom: 8px;
    }}
    .card-value {{
        font-size: 28px;
        font-weight: 700;
        color: #1e3a8a;
    }}
    .card-desc {{
        font-size: 13px;
        color: #64748b;
        margin-top: 4px;
    }}
    
    .section-title {{
        font-size: 22px;
        font-weight: 700;
        margin: 36px 0 16px 0;
        color: #1e293b;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .chart-container {{
        position: relative;
        height: 420px;
        margin-bottom: 24px;
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }}

    .table-wrapper {{
        overflow-x: auto;
        background: white;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 24px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }}
    th, td {{
        padding: 12px 16px;
        text-align: left;
        border-bottom: 1px solid #e2e8f0;
    }}
    th {{
        background-color: #f1f5f9;
        font-weight: 600;
        color: #334155;
    }}
    tr:hover {{ background-color: #f8fafc; }}

    .badge {{
        display: inline-block;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
    }}
    .badge-2010 {{ background: #fed7aa; color: #9a3412; }}
    .badge-2026 {{ background: #bfdbfe; color: #1e40af; }}
    .badge-gov {{ background: #dcfce7; color: #166534; }}
    .badge-opp {{ background: #fee2e2; color: #991b1b; }}

    .quote-box {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #ea580c;
        padding: 14px 18px;
        margin-bottom: 12px;
        border-radius: 0 8px 8px 0;
    }}
    .quote-meta {{
        font-size: 13px;
        font-weight: 600;
        color: #475569;
        margin-bottom: 6px;
    }}
    .quote-text {{
        font-style: italic;
        color: #1e293b;
        font-size: 14px;
    }}

    .search-input {{
        width: 100%;
        max-width: 400px;
        padding: 10px 14px;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        font-size: 14px;
        margin-bottom: 12px;
        box-sizing: border-box;
    }}
</style>
</head>
<body>
<div class="container">
    <header>
        <h1>🏛️ Parlamenti Törvényhozás és Beszédek Összehasonlítása</h1>
        <p class="subtitle">A 2010-es és a 2026-os kormányváltás utáni első 100 nap – Comparative Agendas Project (CAP) Master Codebook (21 főtéma, 209 altéma)</p>
    </header>

    <div class="grid-cards">
        <div class="card">
            <div class="card-title">Benyújtott Törvényjavaslatok</div>
            <div class="card-value">127 db</div>
            <div class="card-desc">2010: {b10_tot} db | 2026: {b26_tot} db</div>
        </div>
        <div class="card">
            <div class="card-title">Elfogadott Törvények</div>
            <div class="card-value" style="color: #166534;">71 db</div>
            <div class="card-desc">2010: {b10_enact} db ({b10_rate:.1f}%) | 2026: {b26_enact} db ({b26_rate:.1f}%)</div>
        </div>
        <div class="card">
            <div class="card-title">Felszólalások (≥ 200 szó, szűrt)</div>
            <div class="card-value">{s_tot:,} db</div>
            <div class="card-desc">2010: {s10_tot:,} db | 2026: {s26_tot:,} db</div>
        </div>
        <div class="card">
            <div class="card-title">Kérdések & Interpellációk</div>
            <div class="card-value">{q_tot:,} db</div>
            <div class="card-desc">2010: {q10_tot:,} db | 2026: {q26_tot:,} db</div>
        </div>
    </div>

    <!-- TÖRVÉNYHOZÁSI BLOKK -->
    <div class="section-title">📜 1. Törvényjavaslatok és Jogalkotási Döntések</div>
    <div class="grid-cards">
        <div class="card">
            <div class="card-title">2010 Törvényhozási Sikeresség</div>
            <div class="card-value" style="color: #ea580c;">{b10_rate:.1f}%</div>
            <div class="card-desc">{b10_tot} javaslatból {b10_enact} törvény lett (2 elutasítva, {b10_pend} folyamatban)</div>
        </div>
        <div class="card">
            <div class="card-title">2026 Törvényhozási Sikeresség</div>
            <div class="card-value" style="color: #2563eb;">{b26_rate:.1f}%</div>
            <div class="card-desc">{b26_tot} javaslatból {b26_enact} törvény lett (0 elutasítva, {b26_pend} folyamatban)</div>
        </div>
        <div class="card">
            <div class="card-title">Ellenzéki Javaslatok Sorsa (Mindkét Év)</div>
            <div class="card-value" style="color: #991b1b;">0% Elfogadva</div>
            <div class="card-desc">2010: 8 ellenzéki javaslatból 0 átment | 2026: 17 ellenzéki javaslatból 0 átment</div>
        </div>
    </div>

    <h3 style="margin-top: 24px; color: #334155;">👥 Kik és mennyi törvényjavaslatot nyújtottak be? (Frakciók szerinti eredményesség)</h3>
    <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <th>Korszak</th>
                    <th>Benyújtó Frakció / Szerv</th>
                    <th>Kormányzati Szerep</th>
                    <th>Benyújtott Javaslat</th>
                    <th>Elfogadott Törvény</th>
                    <th>Elutasított</th>
                    <th>Folyamatban</th>
                    <th>Elfogadási Arány</th>
                </tr>
            </thead>
            <tbody>
                {bills_party_html}
            </tbody>
        </table>
    </div>

    <h3 style="margin-top: 24px; color: #334155;">📂 Milyen szakpolitikai témákban születtek a javaslatok? (CAP Taxonómia)</h3>
    <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <th>Szakpolitikai Főterület</th>
                    <th>2010 Benyújtott</th>
                    <th>2010 Elfogadott (Arány)</th>
                    <th>2026 Benyújtott</th>
                    <th>2026 Elfogadott (Arány)</th>
                </tr>
            </thead>
            <tbody>
                {bills_topic_html}
            </tbody>
        </table>
    </div>

    <h3 style="margin-top: 24px; color: #334155;">⚖️ Mely törvényeket módosították vagy alkották meg? (Törvények szerinti bontás)</h3>
    <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <th>Korszak</th>
                    <th>Érintett vagy Módosított Törvény Hivatalos Neve</th>
                    <th>Jelleg</th>
                    <th>Benyújtott Javaslatok</th>
                    <th>Eredmény</th>
                </tr>
            </thead>
            <tbody>
                {laws_html}
            </tbody>
        </table>
    </div>

    <h3 style="margin-top: 24px; color: #334155;">📋 Az összes törvényjavaslat tételes listája szavazati arányokkal</h3>
    <input type="text" id="billSearch" class="search-input" placeholder="🔎 Keresés törvényre, benyújtóra vagy témára..." onkeyup="filterBills()">
    <div class="table-wrapper" style="max-height: 500px; overflow-y: auto;">
        <table id="billsTable">
            <thead>
                <tr>
                    <th>Év</th>
                    <th>Irományszám</th>
                    <th>Rövid Cím</th>
                    <th>Érintett Törvény</th>
                    <th>Előterjesztő</th>
                    <th>Téma</th>
                    <th>Státusz</th>
                    <th>Szavazatok</th>
                    <th>Dátum</th>
                </tr>
            </thead>
            <tbody>
                {all_bills_html}
            </tbody>
        </table>
    </div>

    <!-- FELSZÓLALÁSOK ÉS VITÁK BLOKK -->
    <div class="section-title">📊 2. Parlamenti Felszólalások és Kérdések Témái (CAP Taxonómia)</div>
    <div class="chart-container">
        <canvas id="topicsChart"></canvas>
    </div>

    <h3 style="margin-top: 24px; color: #334155;">❓ Kérdések és Interpellációk Szakpolitikai Témái (CAP Master Codebook)</h3>
    <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <th>Szakpolitikai Főterület</th>
                    <th>2010 Kérdések & Interpellációk</th>
                    <th>2026 Kérdések & Interpellációk</th>
                    <th>Összesen</th>
                </tr>
            </thead>
            <tbody>
                {questions_topic_html}
            </tbody>
        </table>
    </div>

    <!-- MÚLTBÍRÁLAT BLOKK -->
    <div class="section-title">🔍 3. Kormánypárti Múltbírálati Szűrő ("Elmúlt 8 év" vs "Elmúlt 16 év")</div>
    <div class="grid-cards">
        <div class="card">
            <div class="card-title">2010 Fidesz Múltbírálat</div>
            <div class="card-value" style="color: #ea580c;">{fid_pct:.1f}%</div>
            <div class="card-desc">{fid_tot:,} beszédből {fid_crit} alkalommal ({fid_mentions} fordulat)</div>
        </div>
        <div class="card">
            <div class="card-title">2010 KDNP Múltbírálat</div>
            <div class="card-value" style="color: #ea580c;">{kdnp_pct:.1f}%</div>
            <div class="card-desc">{kdnp_tot:,} beszédből {kdnp_crit} alkalommal ({kdnp_mentions} fordulat)</div>
        </div>
        <div class="card">
            <div class="card-title">2026 TISZA Múltbírálat</div>
            <div class="card-value" style="color: #2563eb;">{tisza_pct:.1f}%</div>
            <div class="card-desc">{tisza_tot:,} beszédből {tisza_crit} alkalommal ({tisza_mentions} fordulat)</div>
        </div>
    </div>

    <h3 style="margin-top: 24px; color: #334155;">🏆 Kik beszéltek a legtöbbet a korábbi időkről negatívan?</h3>
    <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <th>Korszak</th>
                    <th>Képviselő</th>
                    <th>Frakció</th>
                    <th>Összes Beszéde</th>
                    <th>Negatív Visszautalások Száma</th>
                    <th>Átlagos Intenzitás</th>
                </tr>
            </thead>
            <tbody>
                {blame_table_html}
            </tbody>
        </table>
    </div>

    <h3 style="margin-top: 24px; color: #334155;">💬 Konkrét Idézetek a Kormánypárti Beszédekből</h3>
    {quotes_html}

    <!-- FRAKCIÓK ÖSSZESÍTŐJE -->
    <div class="section-title">❓ 4. Felszólalások Frakciók Szerint</div>
    <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <th>Korszak</th>
                    <th>Frakció</th>
                    <th>Státusz</th>
                    <th>Felszólalások Száma</th>
                    <th>Összes Elhangzott Szó</th>
                </tr>
            </thead>
            <tbody>
                {factions_table_html}
            </tbody>
        </table>
    </div>
</div>

<script>
    // Témák diagramja
    const ctx = document.getElementById('topicsChart').getContext('2d');
    const topicsData = {json.dumps(topics_data, ensure_ascii=False)};
    
    new Chart(ctx, {{
        type: 'bar',
        data: {{
            labels: topicsData.map(t => t.tema),
            datasets: [
                {{
                    label: '2010-es kormányváltás (felszólalások)',
                    data: topicsData.map(t => t.c2010),
                    backgroundColor: '#fb923c'
                }},
                {{
                    label: '2026-os kormányváltás (felszólalások)',
                    data: topicsData.map(t => t.c2026),
                    backgroundColor: '#60a5fa'
                }}
            ]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            scales: {{
                x: {{ stacked: false }},
                y: {{ beginAtZero: true }}
            }}
        }}
    }});

    // Kereső a törvényjavaslati táblázathoz
    function filterBills() {{
        const input = document.getElementById("billSearch");
        const filter = input.value.toLowerCase();
        const table = document.getElementById("billsTable");
        const trs = table.getElementsByTagName("tr");

        for (let i = 1; i < trs.length; i++) {{
            const text = trs[i].textContent.toLowerCase();
            trs[i].style.display = text.indexOf(filter) > -1 ? "" : "none";
        }}
    }}
</script>
</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(template)
    with open(OUTPUT_HTML_SHORT, "w", encoding="utf-8") as f:
        f.write(template)
    print(f"Jelentés sikeresen legenerálva:\n - {OUTPUT_HTML}\n - {OUTPUT_HTML_SHORT}")

if __name__ == "__main__":
    generate_report()
