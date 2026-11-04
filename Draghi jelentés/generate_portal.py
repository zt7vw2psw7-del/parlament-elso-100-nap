"""
Script az Európai Parlamenti Draghi-Jelentés Portál (index.html) frissítéséhez.
Hozzáadja a Lisszabon - Letta - Draghi összehasonlító fület,
valamint a 25 fős páneurópai felszólalási adatbázist többdimenziós szűrőkkel.
"""

import sqlite3
import html

DB_PATH = "ep_draghi_database.db"

def build_portal():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Lekérjük az összes felszólalást
    cur.execute("""
        SELECT date, speaker_name, speaker_role, country, political_group, national_party, 
               speech_summary_hu, key_stance, speech_excerpt, official_url
        FROM speeches ORDER BY date ASC, id ASC
    """)
    speeches_data = cur.fetchall()

    # Lekérjük a hivatalos aktusokat
    cur.execute("""
        SELECT procedure_ref, title_hu, act_type, lead_committee, rapporteur, political_group, 
               adoption_date, status, summary_hu, official_url
        FROM official_acts ORDER BY adoption_date ASC
    """)
    acts_data = cur.fetchall()

    # Lekérjük a kérdéseket
    cur.execute("""
        SELECT question_ref, submission_date, question_type, mep_name, political_group, country, 
               subject_hu, answer_summary_hu, official_url
        FROM parliamentary_questions ORDER BY submission_date ASC
    """)
    questions_data = cur.fetchall()

    conn.close()

    html_content = f"""<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Draghi-Jelentés az Európai Parlamentben | Stratégiai Elemző Portál</title>
    <style>
        :root {{
            --primary: #1e3a8a;
            --primary-light: #2563eb;
            --primary-soft: #eff6ff;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --epp: #2563eb;
            --sd: #dc2626;
            --pfe: #1e293b;
            --renew: #d97706;
            --greens: #059669;
            --ecr: #0284c7;
            --left: #991b1b;
            --esn: #475569;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}

        body {{
            background-color: var(--bg);
            color: var(--text-main);
            line-height: 1.6;
            padding: 24px;
        }}

        .container {{
            max-width: 1280px;
            margin: 0 auto;
        }}

        /* Header */
        header {{
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 60%, #1d4ed8 100%);
            color: white;
            padding: 40px 36px;
            border-radius: 18px;
            margin-bottom: 24px;
            box-shadow: 0 12px 30px -5px rgba(15, 23, 42, 0.25);
            position: relative;
            overflow: hidden;
        }}

        header::after {{
            content: '🇪🇺';
            position: absolute;
            right: 30px;
            bottom: -20px;
            font-size: 140px;
            opacity: 0.12;
            pointer-events: none;
        }}

        header h1 {{
            font-size: 2.3rem;
            margin-bottom: 10px;
            font-weight: 800;
            letter-spacing: -0.5px;
        }}

        header p {{
            font-size: 1.12rem;
            color: #cbd5e1;
            max-width: 860px;
        }}

        .header-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 18px;
        }}

        .meta-badge {{
            background: rgba(255, 255, 255, 0.16);
            backdrop-filter: blur(8px);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        /* Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 28px;
        }}

        .stat-card {{
            background: var(--card-bg);
            padding: 22px;
            border-radius: 14px;
            border: 1px solid var(--border);
            box-shadow: 0 4px 6px -2px rgba(0,0,0,0.03);
            display: flex;
            flex-direction: column;
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 16px -4px rgba(0,0,0,0.06);
        }}

        .stat-val {{
            font-size: 2.1rem;
            font-weight: 800;
            color: var(--primary);
            letter-spacing: -1px;
        }}

        .stat-label {{
            color: var(--text-muted);
            font-size: 0.9rem;
            font-weight: 600;
            margin-top: 4px;
        }}

        /* Navigation Tabs */
        .tabs {{
            display: flex;
            gap: 8px;
            margin-bottom: 24px;
            border-bottom: 2px solid var(--border);
            padding-bottom: 10px;
            overflow-x: auto;
        }}

        .tab-btn {{
            background: white;
            border: 1px solid var(--border);
            padding: 10px 18px;
            font-size: 0.93rem;
            font-weight: 600;
            color: var(--text-muted);
            cursor: pointer;
            border-radius: 10px;
            transition: all 0.2s;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .tab-btn:hover {{
            color: var(--primary);
            border-color: var(--primary-light);
            background: var(--primary-soft);
        }}

        .tab-btn.active {{
            color: white;
            background: var(--primary);
            border-color: var(--primary);
            box-shadow: 0 4px 10px -2px rgba(30, 58, 138, 0.3);
        }}

        .tab-content {{
            display: none;
            animation: fadeIn 0.25s ease-in-out;
        }}

        .tab-content.active {{
            display: block;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(4px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Factions Cards */
        .faction-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .faction-card {{
            background: var(--card-bg);
            border-radius: 14px;
            border: 1px solid var(--border);
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.04);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .faction-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 6px;
            height: 100%;
        }}

        .faction-pfe::before {{ background: var(--pfe); }}
        .faction-epp::before {{ background: var(--epp); }}
        .faction-sd::before {{ background: var(--sd); }}
        .faction-greens::before {{ background: var(--greens); }}
        .faction-left::before {{ background: var(--left); }}
        .faction-ecr::before {{ background: var(--ecr); }}
        .faction-renew::before {{ background: var(--renew); }}

        .faction-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}

        .faction-title {{
            font-size: 1.25rem;
            font-weight: 700;
        }}

        .badge {{
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 700;
            color: white;
            letter-spacing: 0.3px;
        }}

        .quote-box {{
            background: #f1f5f9;
            border-left: 3px solid var(--primary-light);
            padding: 12px 16px;
            font-style: italic;
            margin: 14px 0;
            border-radius: 0 8px 8px 0;
            font-size: 0.95rem;
            line-height: 1.5;
        }}

        .quote-author {{
            display: block;
            margin-top: 6px;
            font-style: normal;
            font-weight: 700;
            font-size: 0.82rem;
            color: var(--text-muted);
        }}

        .critique-list {{
            margin-top: 10px;
            padding-left: 20px;
            font-size: 0.92rem;
        }}

        .critique-list li {{
            margin-bottom: 6px;
        }}

        /* Filter Chips */
        .filter-section {{
            background: white;
            padding: 18px 20px;
            border-radius: 12px;
            border: 1px solid var(--border);
            margin-bottom: 18px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .filter-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
        }}

        .filter-label {{
            font-weight: 700;
            font-size: 0.85rem;
            color: var(--text-muted);
            min-width: 90px;
        }}

        .filter-chip {{
            padding: 5px 12px;
            border-radius: 20px;
            border: 1px solid var(--border);
            background: #f8fafc;
            font-size: 0.83rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            color: var(--text-muted);
        }}

        .filter-chip:hover {{
            border-color: var(--primary-light);
            color: var(--primary-light);
            background: white;
        }}

        .filter-chip.active {{
            background: var(--primary-light);
            color: white;
            border-color: var(--primary-light);
        }}

        /* Search Bar & Controls */
        .search-container {{
            display: flex;
            gap: 12px;
            margin-bottom: 16px;
        }}

        .search-bar {{
            flex: 1;
            padding: 12px 18px;
            border-radius: 10px;
            border: 1px solid var(--border);
            font-size: 0.98rem;
            outline: none;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
            transition: border-color 0.2s, box-shadow 0.2s;
        }}

        .search-bar:focus {{
            border-color: var(--primary-light);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
        }}

        .counter-badge {{
            align-self: center;
            font-size: 0.85rem;
            color: var(--text-muted);
            font-weight: 600;
            white-space: nowrap;
        }}

        /* Tables */
        .table-responsive {{
            overflow-x: auto;
            background: white;
            border-radius: 12px;
            border: 1px solid var(--border);
            box-shadow: 0 2px 6px rgba(0,0,0,0.02);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.91rem;
        }}

        th {{
            background: #f8fafc;
            padding: 14px 16px;
            font-weight: 700;
            color: var(--text-muted);
            border-bottom: 2px solid var(--border);
            white-space: nowrap;
        }}

        td {{
            padding: 13px 16px;
            border-bottom: 1px solid var(--border);
            vertical-align: top;
        }}

        tr:hover {{
            background-color: #f8fafc;
        }}

        .btn-link {{
            display: inline-block;
            color: var(--primary-light);
            text-decoration: none;
            font-weight: 600;
            font-size: 0.82rem;
            border: 1px solid #cbd5e1;
            padding: 4px 10px;
            border-radius: 6px;
            transition: all 0.2s;
            white-space: nowrap;
        }}

        .btn-link:hover {{
            background: var(--primary-light);
            color: white;
            border-color: var(--primary-light);
        }}

        .tag-pill {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 0.76rem;
            font-weight: 700;
            margin-right: 4px;
        }}

        .tag-epp {{ background: #dbeafe; color: #1e40af; }}
        .tag-sd {{ background: #fee2e2; color: #991b1b; }}
        .tag-pfe {{ background: #e2e8f0; color: #0f172a; }}
        .tag-renew {{ background: #fef3c7; color: #92400e; }}
        .tag-greens {{ background: #d1fae5; color: #065f46; }}
        .tag-ecr {{ background: #e0f2fe; color: #0369a1; }}
        .tag-left {{ background: #fce7f3; color: #831843; }}
        .tag-esn {{ background: #f1f5f9; color: #334155; }}
        .tag-hu {{ background: #dcfce7; color: #166534; border: 1px solid #86efac; }}

        .faultline-card {{
            background: white;
            padding: 24px;
            border-radius: 12px;
            border: 1px solid var(--border);
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        }}

        .faultline-card h3 {{
            color: var(--primary);
            margin-bottom: 8px;
        }}

        /* Comparison Matrix Styles */
        .comparison-table th {{
            background: #1e3a8a;
            color: white;
            font-size: 0.95rem;
            text-align: center;
        }}

        .comparison-table td {{
            font-size: 0.9rem;
            vertical-align: top;
            padding: 16px;
        }}

        .dimension-col {{
            background: #f8fafc;
            font-weight: 700;
            color: var(--primary);
            width: 18%;
        }}

        .comp-card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
            margin-top: 24px;
        }}

        .comp-card {{
            background: white;
            border-radius: 14px;
            border: 1px solid var(--border);
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.04);
        }}

        .comp-card h4 {{
            font-size: 1.15rem;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* Footer */
        footer {{
            margin-top: 40px;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.9rem;
            padding: 24px;
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }}

        .footer-links a {{
            color: var(--primary-light);
            text-decoration: none;
            font-weight: 600;
            margin-left: 12px;
        }}
    </style>
</head>
<body>

<div class="container">
    <!-- Header -->
    <header>
        <h1>🇪🇺 Európai Parlament – Versenyképességi Stratégiák Portál</h1>
        <p>A Draghi-jelentés (2024), a Letta-jelentés (2024) és a Lisszaboni Stratégia (2000) összehasonlító elemzése, valamint az Európai Parlament páneurópai felszólalásainak és eljárásainak adatbázisa.</p>
        <div class="header-meta">
            <span class="meta-badge">📅 Ciklus: 10. EP (2024–2029)</span>
            <span class="meta-badge">🌐 25 Nemzetközi Felszólalás • 9 Tagállam</span>
            <span class="meta-badge">⚖️ Lisszabon vs. Letta vs. Draghi Összevetés</span>
            <span class="meta-badge">✨ Frissítve: 2026. október</span>
        </div>
    </header>

    <!-- Stats -->
    <div class="stats-grid">
        <div class="stat-card">
            <span class="stat-val">3 Korszak</span>
            <span class="stat-label">Lisszabon ➔ Letta ➔ Draghi</span>
        </div>
        <div class="stat-card">
            <span class="stat-val">25</span>
            <span class="stat-label">Rögzített Európai Felszólalás</span>
        </div>
        <div class="stat-card">
            <span class="stat-val">7</span>
            <span class="stat-label">Hivatalos Eljárás (INI, COD, RSP)</span>
        </div>
        <div class="stat-card">
            <span class="stat-val">800 Mrd €</span>
            <span class="stat-label">Éves Draghi-beruházási Rés</span>
        </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="tabs">
        <button class="tab-btn active" data-tab="factions" onclick="switchTab('factions')">🏛️ Frakciók & Kritikák</button>
        <button class="tab-btn" data-tab="comparison" onclick="switchTab('comparison')">⚖️ Lisszabon vs. Letta vs. Draghi</button>
        <button class="tab-btn" data-tab="speeches" onclick="switchTab('speeches')">📢 Európai Felszólalások (25)</button>
        <button class="tab-btn" data-tab="topics" onclick="switchTab('topics')">📊 3 Fő Topik & Filozófia</button>
        <button class="tab-btn" data-tab="hungarian" onclick="switchTab('hungarian')">🇭🇺 Magyar Dimenzió</button>
        <button class="tab-btn" data-tab="faultlines" onclick="switchTab('faultlines')">⚡ Fő Törésvonalak</button>
        <button class="tab-btn" data-tab="acts" onclick="switchTab('acts')">📜 Hivatalos Aktusok (7)</button>
        <button class="tab-btn" data-tab="questions" onclick="switchTab('questions')">❓ Parlamenti Kérdések (7)</button>
    </div>

    <!-- TAB 1: FACTIONS & CRITICISMS -->
    <div id="tab-factions" class="tab-content active">
        <div class="faction-grid">
            <!-- PfE -->
            <div class="faction-card faction-pfe">
                <div>
                    <div class="faction-header">
                        <span class="faction-title">Patrióták Európáért (PfE)</span>
                        <span class="badge" style="background:#1e293b;">Élesen Elutasító</span>
                    </div>
                    <div class="quote-box">
                        „A Draghi-jelentés olyan milliárdokat követel, amelyek nem léteznek, és amelyeket adósságként hárítanának a jövő nemzedékeire.”
                        <span class="quote-author">— Jordan Bardella, Frakcióvezető (FR)</span>
                    </div>
                    <ul class="critique-list">
                        <li><strong>Közös adósság elutasítása:</strong> A közös uniós hitelt felelőtlen adósságközösségnek (*Transferunion*) tartják.</li>
                        <li><strong>Zöld dogma bírálata:</strong> A gazdasági hanyatlás okaként a brüsszeli tiltásokat és a magas energiaárakat jelölik meg.</li>
                        <li><strong>Nemzeti szuverenitás:</strong> Tiltakoznak a vétójog korlátozása és a minősített többség (QMV) kiterjesztése ellen.</li>
                    </ul>
                </div>
            </div>

            <!-- EPP -->
            <div class="faction-card faction-epp">
                <div>
                    <div class="faction-header">
                        <span class="faction-title">Európai Néppárt (EPP)</span>
                        <span class="badge" style="background:#2563eb;">Támogató / Adósságszkeptikus</span>
                    </div>
                    <div class="quote-box">
                        „A versenyképességet nem újabb állami adóssággal, hanem a magántőke felszabadításával és deregulációval kell elérni.”
                        <span class="quote-author">— Manfred Weber (DE) / Markus Ferber (DE)</span>
                    </div>
                    <ul class="critique-list">
                        <li><strong>Belső vita a hitelről:</strong> A német (CDU/CSU) és északi szárny mereven elutasítja a közös hitelfelvételt.</li>
                        <li><strong>Magántőke elsőbbsége:</strong> A Tőkepiaci Unió (CMU) létrehozását sürgetik az európai megtakarítások mozgósítására.</li>
                        <li><strong>25%-os tehercsökkentés:</strong> Követelik az adminisztratív kötelezettségek (CSRD, CSDDD) drasztikus megkurtítását.</li>
                    </ul>
                </div>
            </div>

            <!-- S&D -->
            <div class="faction-card faction-sd">
                <div>
                    <div class="faction-header">
                        <span class="faction-title">Szocialisták és Demokraták (S&D)</span>
                        <span class="badge" style="background:#dc2626;">Feltételesen Támogató</span>
                    </div>
                    <div class="quote-box">
                        „A versenyképesség nem válhat a munkavállalói jogok és a társadalmi igazságosság leépítésének fedőnevévé.”
                        <span class="quote-author">— Iratxe García Pérez, Frakcióvezető (ES)</span>
                    </div>
                    <ul class="critique-list">
                        <li><strong>Munkajogok védelme:</strong> Tiltakoznak a szociális vívmányok és kollektív szerződések gyengítése ellen.</li>
                        <li><strong>Közös beruházások pártolása:</strong> Támogatják az új európai kötvényeket és a masszív közpénzes beruházásokat.</li>
                        <li><strong>Feltételhez kötött támogatás:</strong> A cégek csak akkor kaphatnak forrást, ha megőrzik a munkahelyeket és tisztességes bért fizetnek.</li>
                    </ul>
                </div>
            </div>

            <!-- Greens/EFA -->
            <div class="faction-card faction-greens">
                <div>
                    <div class="faction-header">
                        <span class="faction-title">Zöldek / EFA (Greens/EFA)</span>
                        <span class="badge" style="background:#059669;">Kritikusan Támogató</span>
                    </div>
                    <div class="quote-box">
                        „A dereguláció nem lehet a környezetvédelmi és klímavédelmi normák lerombolásának trójai fala.”
                        <span class="quote-author">— Bas Eickhout (NL) / Terry Reintke (DE)</span>
                    </div>
                    <ul class="critique-list">
                        <li><strong>Klímacélok védelme:</strong> Aggodalmuk szerint a jobboldal a Green Deal felvizezésére használja a jelentést.</li>
                        <li><strong>Fosszilis bezáródás ellen:</strong> Ellenzik az újabb gázinfrastruktúra és atomenergia túlzott támogatását.</li>
                        <li><strong>Zöld innováció:</strong> A tiszta technológiák fejlesztését tartják Európa egyetlen valódi kitörési pontjának.</li>
                    </ul>
                </div>
            </div>

            <!-- The Left -->
            <div class="faction-card faction-left">
                <div>
                    <div class="faction-header">
                        <span class="faction-title">A Baloldal (The Left)</span>
                        <span class="badge" style="background:#991b1b;">Radikálisan Rendszerkritikus</span>
                    </div>
                    <div class="quote-box">
                        „A jelentés a fegyverkezési ipar és a nagyvállalati oligopóliumok érdekeit szolgálja a dolgozók rovására.”
                        <span class="quote-author">— Manon Aubry, Társelnök (FR)</span>
                    </div>
                    <ul class="critique-list">
                        <li><strong>Militarizáció elutasítása:</strong> Tiltakoznak a védelmi kötvények és fegyvergyártás EU-költségvetésből való tömése ellen.</li>
                        <li><strong>Oligopóliumok veszélye:</strong> Ellenzik a fúziós szabályok lazítását („európai bajnokok”), ami szerintük áremelésekhez vezet.</li>
                    </ul>
                </div>
            </div>

            <!-- Renew -->
            <div class="faction-card faction-renew">
                <div>
                    <div class="faction-header">
                        <span class="faction-title">Megújuló Európa (Renew Europe)</span>
                        <span class="badge" style="background:#d97706;">Erősen Reformpárti</span>
                    </div>
                    <div class="quote-box">
                        „Évente 300 milliárd euró európai megtakarítás áramlik az USA-ba. Ezt a pénzt itthon kell tartanunk!”
                        <span class="quote-author">— Valérie Hayer (FR) / Stéphane Séjourné (FR)</span>
                    </div>
                    <ul class="critique-list">
                        <li><strong>Tőkepiac integrációja:</strong> A nemzeti protekcionizmus azonnali felszámolását követelik a pénzügyi piacokon.</li>
                        <li><strong>Gyorsított döntéshozatal:</strong> A minősített többségi szavazás bevezetését támogatják a gazdasági jogalkotásban.</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <!-- TAB 2: LISBON VS LETTA VS DRAGHI COMPARISON -->
    <div id="tab-comparison" class="tab-content">
        <div style="background:white; padding:28px; border-radius:14px; border:1px solid var(--border); margin-bottom:24px;">
            <h2 style="font-size:1.45rem; color:var(--primary); margin-bottom:10px;">⚖️ A Három Versenyképességi Korszak Összehasonlítása</h2>
            <p style="color:var(--text-muted); margin-bottom:20px;">
                Az Európai Unió gazdaságstratégiájának evolúciója az ezredforduló naiv optimizmusától a belső piac kiteljesítésén át a modern geopolitikai túlélési harcig:
            </p>

            <div class="table-responsive">
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th style="width:16%;">Dimenzió</th>
                            <th style="width:28%; background:#0369a1;">1. Lisszaboni Stratégia (2000)</th>
                            <th style="width:28%; background:#0d9488;">2. Letta-jelentés (2024. április)</th>
                            <th style="width:28%; background:#1e3a8a;">3. Draghi-jelentés (2024. szeptember)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="dimension-col">Dokumentum & Szerző</td>
                            <td><strong>Európai Tanács (Lisszabon)</strong><br><small>2000. március (10 éves terv)</small></td>
                            <td><strong>Enrico Letta</strong><br><small>„Much More Than a Market” (Tanács megbízásából)</small></td>
                            <td><strong>Mario Draghi</strong><br><small>„The Future of European Competitiveness” (Bizottság)</small></td>
                        </tr>
                        <tr>
                            <td class="dimension-col">Fő Célkitűzés & Filozófia</td>
                            <td>„A világ legdinamikusabb és legversenyképesebb tudásalapú gazdasága 2010-re”.<br><strong>Filozófia:</strong> Belső reformok, digitális átállás, szociális kohézió, globalizációs optimizmus.</td>
                            <td>Az Egységes Piac (Single Market) mélyítése és az „5. Szabadság” bevezetése.<br><strong>Filozófia:</strong> Méretgazdaságosság megteremtése a belső fragmentáció felszámolásával.</td>
                            <td>Európa gazdasági és geopolitikai lemaradásának megállítása („Lassú agónia elkerülése”).<br><strong>Filozófia:</strong> Egzisztenciális kihívás, globális iparpolitika, állami szubvenciókra adott válasz.</td>
                        </tr>
                        <tr>
                            <td class="dimension-col">Kormányzás & Módszer</td>
                            <td><strong>Nyitott Koordinációs Módszer (OMC):</strong><br>„Soft law”, nemzeti cselekvési tervek, benchmarking, jogi kikényszeríthetőség és szankciók nélkül.</td>
                            <td><strong>Belső Piaci Jogalkotás:</strong><br>Uniós szintű harmonizáció, nemzeti szabályozási akadályok lebontása az 5. szabadság (kutatás-innováció) jogi beágyazásával.</td>
                            <td><strong>Gyorsított Döntéshozatal & Dereguláció:</strong><br>Minősített többségi szavazás (QMV) kiterjesztése, 25%-os bürokráciacsökkentés (Omnibuszok), Versenyképességi Iránytű.</td>
                        </tr>
                        <tr>
                            <td class="dimension-col">Finanszírozási Modell</td>
                            <td><strong>Nemzeti költségvetések:</strong><br>Előírás a K+F ráfordítások GDP 3%-ára növelésére (többségében elbukott). Nincs közös uniós forrás.</td>
                            <td><strong>Megtakarítási és Beruházási Unió (CMU):</strong><br>Az évi 300 Mrd €-nyi, USA-ba vándorló európai magántőke itthon tartása az egységes pénzügyi piac révén.</td>
                            <td><strong>Közös Hitel + Magántőke:</strong><br>Évi 750–800 Mrd € többletberuházás! Rendszeres közös uniós kötvények (*Safe Assets/Eurobonds*) + EBB tőkeáttétel.</td>
                        </tr>
                        <tr>
                            <td class="dimension-col">Fókuszterületek</td>
                            <td>Információs társadalom, internet-hozzáférés, K+F kutatóhálózatok, rugalmas munkaerőpiac.</td>
                            <td>Távközlés (konszolidáció a 100 szolgáltató helyett), Energiaunió, Pénzügyi integráció, Tudás szabad áramlása.</td>
                            <td>AI és deep-tech, tiszta ipar (Clean Industrial Deal), dekarbonizáció & energiaárak, védelmi ipar és közös beszerzések (EDIP).</td>
                        </tr>
                        <tr>
                            <td class="dimension-col">Miért bukott el / Mi a fő akadály?</td>
                            <td><span style="color:#dc2626; font-weight:700;">Kudarc oka:</span> „Mindenki prioritása, senki felelőssége” (Kok-jelentés, 2004). Nem voltak szankciók, a tagállamok elszabotálták, a 2008-as krízis elsöpörte.</td>
                            <td><span style="color:#d97706; font-weight:700;">Fő akadály:</span> Nemzeti protekcionizmus. A tagállamok féltik a nemzeti bankjaikat, telco cégeiket és energiaóriásaikat a felvásárlásoktól.</td>
                            <td><span style="color:#dc2626; font-weight:700;">Fő akadály:</span> Éles ideológiai ellenállás a német/északi tagállamok és szuverenisták részéről a közös hitellel és a vétójogok leépítésével szemben.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Deep Dive Analysis Cards -->
            <div class="comp-card-grid">
                <div class="comp-card">
                    <h4>🏛️ 1. A Lisszaboni Tanulság: Miért nem működik a „Soft Law”?</h4>
                    <p style="font-size:0.91rem; color:#334155; margin-bottom:10px;">
                        A 2000-ben elfogadott Lisszaboni Stratégia a modern integrációtörténet legnagyobb ígéretéből vált tankönyvi kudarccá. A 2004-es Wim Kok által vezetett félidős felülvizsgálat kíméletlenül rámutatott: a <strong>Nyitott Koordinációs Módszer (OMC)</strong> – amely nem tartalmazott kötelező érvényű jogi normákat, szankciókat és uniós költségvetési fedezetet – alkalmatlan volt a strukturális reformok kikényszerítésére.
                    </p>
                    <p style="font-size:0.91rem; color:#334155;">
                        A tagállamok a „peer review” és a benchmarking ellenére sem hajtották végre a szükséges nemzeti lépéseket, a kitűzött K+F 3%-os GDP-arányos célt Európa 2010-re meg sem közelítette, a 2008-as pénzügyi és euróválság pedig végleg zárójelbe tette a stratégiát.
                    </p>
                </div>

                <div class="comp-card">
                    <h4>🌐 2. A Letta-jelentés: A Belső Méret Megteremtése</h4>
                    <p style="font-size:0.91rem; color:#334155; margin-bottom:10px;">
                        Enrico Letta 2024 áprilisában bemutatott jelentése az egységes belső piac fundamentális újragondolása. Letta diagnózisa szerint Európa gazdasága méretét tekintve felvehetné a versenyt az USA-val, ám <strong>a legfontosabb XXI. századi szektorokban (pénzügy, energia, távközlés) a piac 27 nemzeti darabra van törve</strong>.
                    </p>
                    <p style="font-size:0.91rem; color:#334155;">
                        Letta kulcskoncepciója az <strong>„5. Szabadság”</strong>: a kutatás, az adatok, az innováció és a tudás akadálytalan áramlása. Sürgeti az európai távközlési szektor konszolidációját (az USA 3-4 óriásszolgáltatójával szemben Európában 100 szolgáltató működik) és a Megtakarítási és Beruházási Unió létrehozását, hogy az európaiak pénze ne az amerikai tőzsdéket finanszírozza.
                    </p>
                </div>

                <div class="comp-card">
                    <h4>🛡️ 3. A Draghi-jelentés: A Geopolitikai Túlélés Logikája</h4>
                    <p style="font-size:0.91rem; color:#334155; margin-bottom:10px;">
                        Mario Draghi 2024 szeptemberében nem elégedett meg a belső piaci szabályozás javításával: kíméletlen makroökonómiai diagnózist adott. Szerinte az EU többé nem bízhat abban, hogy a szabályozás önmagában elég, miközben az USA az <em>Inflation Reduction Act (IRA)</em> keretében milliárdos szubvenciókkal szívja el a cégeket, Kína pedig állami kapitalizmussal árasztja el a piacot.
                    </p>
                    <p style="font-size:0.91rem; color:#334155;">
                        Draghi válasza drasztikus: évi 800 milliárd eurós beruházási sokk, új közös uniós kötvénypiac (*Safe Assets*), 25%-os adminisztratív tehermentesítés és döntéshozatali sebesség. A jelentés lényege: <em>„integráció, vagy lassú agónia”</em>.
                    </p>
                </div>
            </div>

            <!-- Symbiosis Box -->
            <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:12px; padding:20px; margin-top:24px;">
                <h4 style="color:#1e3a8a; margin-bottom:8px;">🔗 A Két 2024-es Jelentés Szimbiózisa: Letta + Draghi</h4>
                <p style="font-size:0.93rem; color:#1e40af; line-height:1.7;">
                    A két olasz ex-miniszterelnök munkája nem riválisa, hanem feltétele egymásnak:  
                    • <strong>Letta a belső méretet teremti meg:</strong> lebontja a 27 nemzeti piac korlátait a távközlésben, energiában és tőkepiacon, hogy megszülessenek az európai léptékű vállalatok.  
                    • <strong>Draghi a külső pajzsot és az üzemanyagot biztosítja:</strong> mozgósítja az évi 800 milliárd eurós tőkét, védi a stratégiai ágazatokat a tisztességtelen globális versenytől, és felgyorsítja a döntéshozatalt.  
                    <em>„Letta nélkül Draghi 800 milliárd eurója egy széttöredezett, szivárgó piacra ömlene; Draghi nélkül Letta egységes piaca tőke- és energiahiányosan vérezne el a globális versenyben.”</em>
                </p>
            </div>
        </div>
    </div>

    <!-- TAB 3: EUROPEAN SPEECHES (25) -->
    <div id="tab-speeches" class="tab-content">
        <!-- Filter Controls -->
        <div class="filter-section">
            <div class="filter-row">
                <span class="filter-label">🌍 Ország szerint:</span>
                <button class="filter-chip active" onclick="filterCountry('all')">Összes ország</button>
                <button class="filter-chip" onclick="filterCountry('Németország')">🇩🇪 Németország (5)</button>
                <button class="filter-chip" onclick="filterCountry('Franciaország')">🇫🇷 Franciaország (4)</button>
                <button class="filter-chip" onclick="filterCountry('Olaszország')">🇮🇹 Olaszország (4)</button>
                <button class="filter-chip" onclick="filterCountry('Spanyolország')">🇪🇸 Spanyolország (3)</button>
                <button class="filter-chip" onclick="filterCountry('Lengyelország')">🇵🇱 Lengyelország (1)</button>
                <button class="filter-chip" onclick="filterCountry('Románia')">🇷🇴 Románia (1)</button>
                <button class="filter-chip" onclick="filterCountry('Belgium')">🇧🇪 Belgium (1)</button>
                <button class="filter-chip" onclick="filterCountry('Hollandia')">🇳🇱 Hollandia (1)</button>
                <button class="filter-chip" onclick="filterCountry('Magyarország')">🇭🇺 Magyarország (5)</button>
            </div>
            <div class="filter-row">
                <span class="filter-label">🏛️ Frakció szerint:</span>
                <button class="filter-chip active" onclick="filterGroup('all')">Összes frakció</button>
                <button class="filter-chip" onclick="filterGroup('EPP')">EPP (7)</button>
                <button class="filter-chip" onclick="filterGroup('S&D')">S&D (4)</button>
                <button class="filter-chip" onclick="filterGroup('PfE')">PfE (4)</button>
                <button class="filter-chip" onclick="filterGroup('Renew')">Renew (2)</button>
                <button class="filter-chip" onclick="filterGroup('Greens/EFA')">Greens/EFA (2)</button>
                <button class="filter-chip" onclick="filterGroup('ECR')">ECR (2)</button>
                <button class="filter-chip" onclick="filterGroup('The Left')">The Left (1)</button>
                <button class="filter-chip" onclick="filterGroup('ESN')">ESN (1)</button>
            </div>
        </div>

        <div class="search-container">
            <input type="text" id="speechesSearch" class="search-bar" placeholder="🔍 Keresés képviselő, ország, párt vagy beszédkivonat alapján..." onkeyup="filterSpeechesTable()">
            <span id="speechesCount" class="counter-badge">25 felszólalás látható</span>
        </div>

        <div class="table-responsive">
            <table id="speechesTable">
                <thead>
                    <tr>
                        <th>Dátum</th>
                        <th>Felszólaló</th>
                        <th>Frakció / Tisztség</th>
                        <th>Ország</th>
                        <th>Álláspont / Fókusz</th>
                        <th>Beszédkivonat / Idézet</th>
                        <th>Dokumentum</th>
                    </tr>
                </thead>
                <tbody>
"""

    for row in speeches_data:
        date, name, role, country, group, party, summary, stance, excerpt, url = row
        
        # Tag class mapping
        tag_cls = "tag-pfe"
        g_upper = group.upper()
        if "EPP" in g_upper: tag_cls = "tag-epp"
        elif "S&D" in g_upper: tag_cls = "tag-sd"
        elif "RENEW" in g_upper: tag_cls = "tag-renew"
        elif "GREEN" in g_upper: tag_cls = "tag-greens"
        elif "ECR" in g_upper: tag_cls = "tag-ecr"
        elif "LEFT" in g_upper: tag_cls = "tag-left"
        elif "ESN" in g_upper: tag_cls = "tag-esn"

        html_content += f"""                    <tr data-country="{html.escape(country)}" data-group="{html.escape(group)}">
                        <td style="white-space:nowrap;">{html.escape(date)}</td>
                        <td><strong>{html.escape(name)}</strong></td>
                        <td><span class="tag-pill {tag_cls}">{html.escape(group)}</span><br><small style="color:var(--text-muted);">{html.escape(role)}</small></td>
                        <td>{html.escape(country)}</td>
                        <td><strong>{html.escape(stance)}</strong></td>
                        <td>„{html.escape(excerpt)}”<br><small style="color:var(--text-muted);">{html.escape(summary)}</small></td>
                        <td><a class="btn-link" target="_blank" href="{html.escape(url)}">CRE ↗</a></td>
                    </tr>\n"""

    html_content += """                </tbody>
            </table>
        </div>
    </div>

    <!-- TAB 4: TOPICS & POLITICAL PHILOSOPHY -->
    <div id="tab-topics" class="tab-content">
        <!-- Distribution Header -->
        <div style="background:white; padding:28px; border-radius:14px; border:1px solid var(--border); margin-bottom:24px;">
            <h2 style="font-size:1.4rem; color:var(--primary); margin-bottom:10px;">📊 A Három Fő Problémakör Megoszlása az EP Vitáiban és Aktusaiban</h2>
            <p style="color:var(--text-muted); margin-bottom:24px;">
                A Draghi-jelentéssel foglalkozó plenáris viták, képviselői felszólalások és hivatalos eljárások elemzése alapján az alábbi relatív arányban jelent meg a három kulcstéma:
            </p>

            <div style="margin-bottom:20px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:6px; font-weight:700;">
                    <span>1. Bürokrácia, túlszabályozás (AI Act, GDPR, CSRD) & Innováció</span>
                    <span style="color:var(--primary-light);">kb. 40% (Leggyakoribb téma)</span>
                </div>
                <div style="background:#e2e8f0; border-radius:10px; height:20px; overflow:hidden;">
                    <div style="background:linear-gradient(90deg, #2563eb, #0ea5e9); width:40%; height:100%; border-radius:10px;"></div>
                </div>
                <small style="color:var(--text-muted);">Szinte minden felszólaló érintette (EPP, ECR, PfE a dereguláció mellett, Zöldek és S&D a normák védelmében).</small>
            </div>

            <div style="margin-bottom:20px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:6px; font-weight:700;">
                    <span>2. A finanszírozás makroökonómiai realitásai (800 Mrd €, Eurobonds, CMU)</span>
                    <span style="color:#dc2626;">kb. 38% (Legélesebb polarizáció)</span>
                </div>
                <div style="background:#e2e8f0; border-radius:10px; height:20px; overflow:hidden;">
                    <div style="background:linear-gradient(90deg, #dc2626, #f59e0b); width:38%; height:100%; border-radius:10px;"></div>
                </div>
                <small style="color:var(--text-muted);">A legvitatottabb kérdés: közös hitelfelvétel (Safe Assets) vs. magántőke és Tőkepiaci Unió.</small>
            </div>

            <div style="margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:6px; font-weight:700;">
                    <span>3. Intézményi és kormányzási reformok elmélyítése (QMV, vétójog, sebesség)</span>
                    <span style="color:#059669;">kb. 22% (Alkotmányos fókusz)</span>
                </div>
                <div style="background:#e2e8f0; border-radius:10px; height:20px; overflow:hidden;">
                    <div style="background:linear-gradient(90deg, #059669, #10b981); width:22%; height:100%; border-radius:10px;"></div>
                </div>
                <small style="color:var(--text-muted);">Főleg az AFCO szakbizottságban (2025/2013(INI)) és a szuverenitási elvi vitákban került előtérbe.</small>
            </div>
        </div>

        <!-- Detailed Theoretical Deep Dives -->
        <div style="display:grid; grid-template-columns:1fr; gap:20px; margin-bottom:30px;">
            <!-- Topic 1 -->
            <div class="faultline-card" style="border-left: 6px solid #2563eb;">
                <h3 style="color:#1e3a8a;">🏛️ 1. A Bürokrácia és Túlszabályozás Innovációt Gátló Hatása & Politikai Filozófia</h3>
                <p><strong>A parlamenti valóság:</strong> A képviselők a „szabályozói gúzsbakötést” jelölték meg a technológiai lemaradás fő okaként. Kiemelt célpontok: a mesterséges intelligencia korai korlátozása (AI Act), a digitális adatfelhasználás szigora (GDPR) és a kkv-kat bénító fenntarthatósági jelentések (CSRD, CSDDD).</p>
                
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:18px; margin-top:14px;">
                    <h4 style="color:#0f172a; margin-bottom:10px;">🧠 Politikai Filozófiai és Államelméleti Keret:</h4>
                    <ul style="padding-left:20px; font-size:0.93rem; color:#334155; line-height:1.7;">
                        <li><strong>Max Weber és a bürokrácia „vasrecéje” (Iron Cage):</strong> A modern államigazgatás túlracionalizálódása olyan zárt jogi gépezetté válik, amely önmagát termeli újra. Brüsszel a szabályozásban találja meg saját létének igazolását („szabályozói birodalom”), függetlenül annak gazdasági költségeitől.</li>
                        <li><strong>F. A. Hayek és a „végzetes elbizakodottság” (The Fatal Conceit):</strong> Az állami jogalkotó soha nem rendelkezhet azzal a decentralizált, dinamikus piaci tudással, amivel a vállalkozók. Az AI Act ex-ante (előzetes, kategóriákba szorító) szabályozása megbénítja a spontán piaci innovációt.</li>
                        <li><strong>Joseph Schumpeter és a „teremtő rombolás” (Creative Destruction):</strong> Az európai modell a meglévő status quo, a bejáratott vállalatok és a kockázatkerülés védelmére van optimalizálva. A túlszabályozás pont azt az agresszív piaci belépést és dinamizmust gátolja, ami a Szilícium-völgy sikerének alapja.</li>
                        <li><strong>Az „Elővigyázatossági Állam” (Precautionary State) koncepciója:</strong> Európa a kockázatkezelés szuperhatalma lett: ahelyett, hogy megteremtené az innováció feltételeit, minden lehetséges kockázatot előre jogszabályba próbál zárni.</li>
                    </ul>
                </div>
            </div>

            <!-- Topic 2 -->
            <div class="faultline-card" style="border-left: 6px solid #dc2626;">
                <h3 style="color:#991b1b;">💶 2. A Finanszírozás Makroökonómiai Realitásai</h3>
                <p><strong>A parlamenti valóság:</strong> A vita középpontjában Draghi száma áll: évi **750–800 milliárd euró** többletberuházás kell (az EU GDP közel 5%-a). Összecsaptak a fiskális realisták, a hitelpártiak és a tőkepiaci liberálisok.</p>
                
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:18px; margin-top:14px;">
                    <h4 style="color:#0f172a; margin-bottom:10px;">🔍 A Makroökonómiai Trilemma az EP-ben:</h4>
                    <ul style="padding-left:20px; font-size:0.93rem; color:#334155; line-height:1.7;">
                        <li><strong>1. A Stabilitási Paktum fiskális fékje:</strong> A magas adósságú tagállamok nem képesek nemzeti büdzséből forrást biztosítani túlzottdeficit-eljárás kockázata nélkül.</li>
                        <li><strong>2. Közös adósság (*Eurobonds / Safe Assets*):</strong> Az S&D és déli tagállamok szerint elengedhetetlen; a német/északi befizetők és a Patrióták morális kockázatként és adósságcsapdaként elutasítják.</li>
                        <li><strong>3. Tőkepiaci és Megtakarítási Unió (CMU mint kompromisszum):</strong> Az évi **300 milliárd eurónyi európai megtakarítás Amerikába áramlását** kell megfékezni az egységes európai tőkepiac révén.</li>
                    </ul>
                </div>
            </div>

            <!-- Topic 3 -->
            <div class="faultline-card" style="border-left: 6px solid #059669;">
                <h3 style="color:#065f46;">⚖️ 3. Intézményi és Kormányzási Reformok Elmélyítése</h3>
                <p><strong>A parlamenti valóság:</strong> Mario Draghi szerint Európa döntéshozatala túl lassú (átlagos jogalkotási átfutási idő: 19–24 hónap) a hónapok alatt változó geopolitikai térben.</p>
                
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:18px; margin-top:14px;">
                    <h4 style="color:#0f172a; margin-bottom:10px;">🏛️ Közpolitikai és Alkotmányos Tét:</h4>
                    <ul style="padding-left:20px; font-size:0.93rem; color:#334155; line-height:1.7;">
                        <li><strong>Minősített többségi szavazás (QMV) vs. Vétójog:</strong> A 2025/2013(INI) AFCO-jelentésben a szavazati jogok kiterjesztését szorgalmazzák a nemzeti vétók helyett.</li>
                        <li><strong>Horizontális Ipari Koordináció (Competitiveness Compass):</strong> A Bizottság belső széttagoltságának megszüntetése, erős ügyvezető alelnöki struktúra.</li>
                        <li><strong>Differenciált integráció („Koalíciók a hajlandókból”):</strong> Ha a 27-ek nem tudnak megegyezni, a haladni akaró országok szűkebb köre léphet előre.</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <!-- TAB 5: HUNGARIAN DIMENSION -->
    <div id="tab-hungarian" class="tab-content">
        <div style="background:white; padding:24px; border-radius:14px; border:1px solid var(--border); margin-bottom:24px;">
            <h2 style="font-size:1.35rem; color:var(--primary); margin-bottom:8px;">🇭🇺 A Magyar Dimenzió a Draghi-Vitákban</h2>
            <p style="color:var(--text-muted); margin-bottom:16px;">
                A Draghi-jelentés megjelenése egybeesett a 2024. második félévi <strong>Magyar EU Tanácsi Elnökséggel</strong>, amelynek hivatalos záródokumentuma a <em>„Budapesti Nyilatkozat az Új Európai Versenyképességi Megállapodásról”</em> (2024. november 8.) volt. A magyar képviselők élesen megosztottak a megvalósítás módjában:
            </p>

            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:16px;">
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:16px;">
                    <span class="tag-pill tag-pfe">PfE / Fidesz</span>
                    <h4 style="margin:8px 0 4px 0;">Szuverenista & Energiaár-fókusz</h4>
                    <p style="font-size:0.88rem; color:#475569;">
                        <strong>Orbán Viktor, Gál Kinga, Dömötör Csaba, Gyürk András:</strong> Elfogadják a hanyatlás diagnózisát, de a szankciós politikát és a zöld dogmatizmust teszik felelőssé. Elutasítják a közös hitelt és a vétójog korlátozását.
                    </p>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:16px;">
                    <span class="tag-pill tag-epp">EPP / Tisza Párt</span>
                    <h4 style="margin:8px 0 4px 0;">Jogállamiság & CEE KKV-fókusz</h4>
                    <p style="font-size:0.88rem; color:#475569;">
                        <strong>Magyar Péter:</strong> Versenyképesség nem létezhet jogbiztonság, oktatás és innováció nélkül. Írásbeli kérdésben kérte számon a források eljuttatását a CEE KKV-khoz.
                    </p>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:16px;">
                    <span class="tag-pill tag-sd">S&D / DK</span>
                    <h4 style="margin:8px 0 4px 0;">Közös Európai Beruházások & Bérfelzárkózás</h4>
                    <p style="font-size:0.88rem; color:#475569;">
                        <strong>Dobrev Klára:</strong> A közös uniós források és az integráció elmélyítése mellett érvel; elutasítja az olcsó munkaerőre épülő gazdaságmodellt.
                    </p>
                </div>
            </div>
        </div>
    </div>

    <!-- TAB 6: FAULT LINES -->
    <div id="tab-faultlines" class="tab-content">
        <div class="faultline-card">
            <h3>1. Közös Uniós Adósságkibocsátás (Eurobonds / Safe Assets)</h3>
            <p><strong>A kérdés:</strong> Mario Draghi évi 750–800 milliárd eurós pótlólagos beruházást tart szükségesnek, amit részben rendszeres közös uniós kötvénnyel finanszírozna.</p>
            <p style="margin-top:8px;"><strong>Törésvonal:</strong> Az S&D, a Renew és a déli tagállamok támogatják. Az EPP német/északi tagjai, az ECR, valamint a PfE határozottan elutasítják az állandósított közös garanciavállalást.</p>
        </div>

        <div class="faultline-card">
            <h3>2. Dereguláció vs. Környezetvédelmi és Szociális Vívmányok</h3>
            <p><strong>A kérdés:</strong> A jelentés a jelentéstételi kötelezettségek 25%-os csökkentését és a döntéshozatal gyorsítását sürgeti.</p>
            <p style="margin-top:8px;"><strong>Törésvonal:</strong> A jobbközép és jobboldali pártok (EPP, ECR, PfE) ezt a fenntarthatósági szabályok (CSRD, CSDDD) megnyirbálására használják. A Zöldek és az S&D ezt vörös vonalnak tekintik.</p>
        </div>

        <div class="faultline-card">
            <h3>3. Regionális Aszimmetria: Nyugati Óriások vs. Közép-Kelet-Európai KKV-k</h3>
            <p><strong>A kérdés:</strong> Az állami támogatási szabályok lazítása és az Európai Versenyképességi Alap felállítása.</p>
            <p style="margin-top:8px;"><strong>Törésvonal:</strong> A közép- és kelet-európai képviselők arra figyelmeztetnek, hogy az állami támogatások lazítása a gazdag magállamoknak (főleg Németországnak és Franciaországnak) kedvez a periféria kárára.</p>
        </div>
    </div>

    <!-- TAB 7: OFFICIAL ACTS -->
    <div id="tab-acts" class="tab-content">
        <div class="search-container">
            <input type="text" id="actsSearch" class="search-bar" placeholder="🔍 Keresés eljáráskód, cím, eljárástípus vagy bizottság alapján..." onkeyup="filterTable('actsTable', 'actsSearch', 'actsCount')">
            <span id="actsCount" class="counter-badge">7 eljárás</span>
        </div>
        <div class="table-responsive">
            <table id="actsTable">
                <thead>
                    <tr>
                        <th>Hivatkozás</th>
                        <th>Cím (Magyarul)</th>
                        <th>Típus</th>
                        <th>Bizottság</th>
                        <th>Előadó / Frakció</th>
                        <th>Dátum & Státusz</th>
                        <th>Dokumentum</th>
                    </tr>
                </thead>
                <tbody>
"""

    for act in acts_data:
        pref, title, atype, comm, rapp, grp, date, status, summary, url = act
        status_color = "#059669" if "Elfogadva" in status else "#d97706"
        html_content += f"""                    <tr>
                        <td><strong>{html.escape(pref)}</strong></td>
                        <td>{html.escape(title)}</td>
                        <td>{html.escape(atype)}</td>
                        <td>{html.escape(comm)}</td>
                        <td>{html.escape(rapp)} <span class="tag-pill tag-epp">{html.escape(grp)}</span></td>
                        <td>{html.escape(date)}<br><span style="color:{status_color};font-weight:700;">{html.escape(status)}</span></td>
                        <td><a class="btn-link" target="_blank" href="{html.escape(url)}">Megtekintés ↗</a></td>
                    </tr>\n"""

    html_content += """                </tbody>
            </table>
        </div>
    </div>

    <!-- TAB 8: QUESTIONS -->
    <div id="tab-questions" class="tab-content">
        <div class="search-container">
            <input type="text" id="questionsSearch" class="search-bar" placeholder="🔍 Keresés kérdéskód, képviselő vagy kulcsszó alapján..." onkeyup="filterTable('questionsTable', 'questionsSearch', 'questionsCount')">
            <span id="questionsCount" class="counter-badge">7 kérdés</span>
        </div>
        <div class="table-responsive">
            <table id="questionsTable">
                <thead>
                    <tr>
                        <th>Azonosító</th>
                        <th>Dátum</th>
                        <th>Képviselő</th>
                        <th>Frakció / Ország</th>
                        <th>Kérdés Tárgya</th>
                        <th>A Bizottság / Tanács Válasza</th>
                        <th>Dokumentum</th>
                    </tr>
                </thead>
                <tbody>
"""

    for q in questions_data:
        qref, qdate, qtype, mep, qgrp, qctry, subj, ans, qurl = q
        html_content += f"""                    <tr>
                        <td><strong>{html.escape(qref)}</strong></td>
                        <td>{html.escape(qdate)}</td>
                        <td>{html.escape(mep)}</td>
                        <td><span class="tag-pill tag-pfe">{html.escape(qgrp)}</span> {html.escape(qctry)}</td>
                        <td>{html.escape(subj)}</td>
                        <td>{html.escape(ans)}</td>
                        <td><a class="btn-link" target="_blank" href="{html.escape(qurl)}">Megtekintés ↗</a></td>
                    </tr>\n"""

    html_content += """                </tbody>
            </table>
        </div>
    </div>

    <!-- Footer -->
    <footer>
        <div>Európai Parlamenti Draghi-Jelentés Adatbázis és Elemző Portál • 10. Parlamenti Ciklus (2024–2029)</div>
        <div class="footer-links">
            <a href="javascript:window.print()">🖨️ Nyomtatás / PDF</a>
        </div>
    </footer>
</div>

<script>
    // Tab switching
    function switchTab(tabId) {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            if (btn.getAttribute('data-tab') === tabId) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        document.querySelectorAll('.tab-content').forEach(content => {
            if (content.id === 'tab-' + tabId) {
                content.classList.add('active');
            } else {
                content.classList.remove('active');
            }
        });
    }

    // Generic table filter
    function filterTable(tableId, inputId, counterId) {
        var filter = document.getElementById(inputId).value.toLowerCase();
        var tr = document.getElementById(tableId).getElementsByTagName("tr");
        var visibleCount = 0;

        for (var i = 1; i < tr.length; i++) {
            var text = tr[i].textContent.toLowerCase();
            if (text.indexOf(filter) > -1) {
                tr[i].style.display = "";
                visibleCount++;
            } else {
                tr[i].style.display = "none";
            }
        }
        if (counterId) {
            document.getElementById(counterId).textContent = visibleCount + " találat";
        }
    }

    // State for Speeches filtering
    var currentCountryFilter = 'all';
    var currentGroupFilter = 'all';

    function filterCountry(country) {
        currentCountryFilter = country;
        // Update active class on country chips
        var container = event.currentTarget.parentElement;
        container.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
        event.currentTarget.classList.add('active');
        applySpeechesFilter();
    }

    function filterGroup(group) {
        currentGroupFilter = group;
        // Update active class on group chips
        var container = event.currentTarget.parentElement;
        container.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
        event.currentTarget.classList.add('active');
        applySpeechesFilter();
    }

    function filterSpeechesTable() {
        applySpeechesFilter();
    }

    function applySpeechesFilter() {
        var search = document.getElementById("speechesSearch").value.toLowerCase();
        var table = document.getElementById("speechesTable");
        var tr = table.getElementsByTagName("tr");
        var visible = 0;

        for (var i = 1; i < tr.length; i++) {
            var row = tr[i];
            var rCountry = row.getAttribute("data-country") || "";
            var rGroup = row.getAttribute("data-group") || "";
            var text = row.textContent.toLowerCase();

            var matchesCountry = (currentCountryFilter === 'all') || (rCountry === currentCountryFilter);
            var matchesGroup = (currentGroupFilter === 'all') || (rGroup.indexOf(currentGroupFilter) > -1);
            var matchesSearch = (search === "") || (text.indexOf(search) > -1);

            if (matchesCountry && matchesGroup && matchesSearch) {
                row.style.display = "";
                visible++;
            } else {
                row.style.display = "none";
            }
        }

        document.getElementById("speechesCount").textContent = visible + " felszólalás látható";
    }
</script>

</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    with open("draghi_dashboard.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("index.html and draghi_dashboard.html generated successfully.")

if __name__ == "__main__":
    build_portal()
