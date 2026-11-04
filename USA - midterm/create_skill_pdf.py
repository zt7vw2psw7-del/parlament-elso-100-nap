#!/usr/bin/env python3
"""
create_skill_pdf.py - Generates the complete, official PDF and printable HTML
documentation for the Election Tracker Skill.
"""

import os
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.join(BASE_DIR, ".agent", "skills", "election-tracker")
PDF_OUTPUT_PATH = os.path.join(BASE_DIR, "ELECTION_TRACKER_SKILL.pdf")
SKILL_PDF_PATH = os.path.join(SKILL_DIR, "SKILL.pdf")
HTML_OUTPUT_PATH = os.path.join(BASE_DIR, "SKILL_DOCUMENTATION.html")

DOCUMENT_CONTENT = """================================================================================
         ELECTION TRACKER SKILL (VÁLASZTÁSI PORTÁL ÉPÍTŐ ÉS MONITOR)
                  HIVATALOS SPECIFIKÁCIÓ ÉS RENDSZERÚTMUTATÓ
================================================================================

Kiadás dátuma: 2026. Október
Verzió: 2.0 (Univerzális Nemzetközi Kiadás)
Típus: Antigravity Agent Skill (.agent/skills/election-tracker)
Licenc: Nyílt és szabadon adaptálható bármely országra


1. A SKILL CÉLJA ÉS ÁTTEKINTÉSE
--------------------------------------------------------------------------------
Az "election-tracker" egy átfogó, adatvezérelt mesterséges intelligencia képesség 
(skill), amely felkészíti a rendszert professzionális, interaktív és szigorúan 
hiteles választási portálok generálására BÁRMELY ORSZÁG számára (pl. USA, Németország, 
Egyesült Királyság, Magyarország, Franciaország, Lengyelország stb.).

A portál architektúrája 5 alappillérre épül:
  1. Grafikus mandátumbecslések (Interaktív félköríves parlament és többségi mérleg).
  2. Akkreditált közvélemény-kutatási adatbázis és súlyozott átlagok (A+, A, B+).
  3. Országos médiafigyelő és kulcsszó-gyakorisági trendelemző (Daily & Weekly digest).
  4. Vezető politikus monitor (Truth Social/X posztok, tényellenőrzés, nagygyűlések).
  5. Teljesen automatizált napi adatfrissítő motor (Python és ütemezett cron).


2. NEMZETKÖZI PARLAMENTI SPECIFIKÁCIÓK
--------------------------------------------------------------------------------
A skill az alábbi országok törvényhozási és választási szabályait tartalmazza:

Ország              Törvényhozás             Összes Szék    Többségi Küszöb
--------------------------------------------------------------------------------
USA                 Szenátus (Felsőház)         100           51 mandátum
USA                 Képviselőház (Alsóház)      435          218 mandátum
Németország         Bundestag                   630          316 mandátum (5% gát)
Egyesült Királyság  House of Commons            650          326 mandátum (FPTP)
Magyarország        Országgyűlés                199          100 (133 kétharmad)
Franciaország       Assemblée Nationale         577          289 mandátum
Lengyelország       Sejm (Alsóház)              460          231 mandátum
--------------------------------------------------------------------------------


3. MEGBÍZHATÓSÁGI KRITÉRIUMOK ÉS TIER-1 FORRÁSOK
--------------------------------------------------------------------------------
A skill szigorú szabályokat alkalmaz a dezinformáció és a félrevezetés ellen:

A. KÖZVÉLEMÉNY-KUTATÓI MINŐSÍTÉSEK (POLLSTER GRADES):
   * A+ Minősítés: Szigorú kettős ellenőrzésű véletlenszerű mintavétel, teljes
     módszertani transzparencia (pl. Siena College/NYT, Infratest dimap).
   * A / A- Minősítés: Vezető független akadémiai intézetek és hibrid mintavétel
     (pl. Marist Poll, YouGov, Forschungsgruppe Wahlen, Medián, 21 Kutatóközpont).
   * B+ Minősítés: Nemzetközi minősített online panelek (pl. Ipsos, Forsa, Závecz).
   * Kizárva: Pártfinanszírozott belső mérések és nem reprezentatív szavazások.

B. HITELES MÉDIAVÁLOGATÁS (TIER-1 MEDIA):
   * USA / Globális: Associated Press (AP), Reuters, BBC News, The New York Times,
     The Wall Street Journal, Politico, PBS NewsHour.
   * Európa: DPA (Németország), AFP (Franciaország), PA Media (UK).
   * Magyarország: Telex, 24.hu, HVG, 444 (szerkesztőségi ellenőrzött hírek).


4. GRAFIKAI MOTOR ÉS INFOGRAFIKA
--------------------------------------------------------------------------------
A skill beépített SVG motort tartalmaz, amely nem igényel külső nehéz könyvtárakat:
  * Koncentrikus félköríves parlament (Hemicycle):
    Képlet: x = X0 + R * cos(theta), y = Y0 - R * sin(theta)
  * Minden mandátumhoz tartozik egy kattintható / lebegő kártya:
    - Nem választó székek: hivatalban lévő képviselő/szenátor neve, mandátum vége.
    - Választási székek: korábbi képviselő, induló jelöltek, várható esélyes.
  * Szegmentált többségi mérleg (Biztos, Valószínű, Hajló, Csatatér kategóriák).


5. HÍRELEMZÉS ÉS VEZETŐ POLITIKUS FIGYELŐ
--------------------------------------------------------------------------------
  * Kulcsszó-elemzés: A hírek szövegéből kinyert leggyakoribb kifejezések felhője.
  * A Nap Kiemelt Témája: Automatikusan szűrt legmagasabb hatású (impact score) hír.
  * Heti Összefoglaló: 4 kulcsfontosságú stratégiai tanulság és elemzői konszenzus.
  * Vezető Politikus Monitor:
    - Közösségi és hivatalos bejegyzések időrendi folyama.
    - Független tényellenőrzés (AP / Reuters Fact-Check) minden poszt mellé.
    - Kampányállomások és nagygyűlések naptára.
    - Elnöki / Kormányfői népszerűségi mutató (Approval Rating).


6. HASZNÁLATI ÚTMUTATÓ ÉS PARANCSOK
--------------------------------------------------------------------------------
A skill kétféleképpen alkalmazható:

1. Chat Parancs az AI-nak:
   "Készíts nekem egy választási portált Németországra az election-tracker skill alapján!"

2. Parancssori Generálás a Mellékelt Eszközzel:
   python3 .agent/skills/election-tracker/scripts/scaffold_country.py --country hungary --output ~/Desktop/Valasztas-HU
   python3 .agent/skills/election-tracker/scripts/scaffold_country.py --country germany --output ~/Desktop/Bundestag2025
   python3 .agent/skills/election-tracker/scripts/scaffold_country.py --country uk --output ~/Desktop/UKElection

7. FÁJLSZERKEZET
--------------------------------------------------------------------------------
.agent/skills/election-tracker/
  ├── SKILL.md                          # Fő képességfájl (frontmatter & instrukciók)
  ├── scripts/
  │   └── scaffold_country.py           # Univerzális több-országos generáló motor
  └── references/
      ├── country_parliaments.md        # Nemzetközi parlamenti méretek & szabályok
      └── trusted_sources_guide.md      # Hiteles média és közvélemény-kutató kritériumok

================================================================================
                        DOKUMENTÁCIÓ VÉGE • ANTIGRAVITY
================================================================================
"""

def generate_pdf():
    txt_temp_path = os.path.join(BASE_DIR, "temp_skill_doc.txt")
    with open(txt_temp_path, "w", encoding="utf-8") as f:
        f.write(DOCUMENT_CONTENT)

    # Use cupsfilter to convert to professional PDF
    cmd = f'cupsfilter -m application/pdf "{txt_temp_path}" > "{PDF_OUTPUT_PATH}" 2>/dev/null'
    subprocess.run(cmd, shell=True, check=True)
    
    # Copy to skill folder as well
    subprocess.run(f'cp "{PDF_OUTPUT_PATH}" "{SKILL_PDF_PATH}"', shell=True, check=True)

    if os.path.exists(txt_temp_path):
        os.remove(txt_temp_path)

    print(f"✅ PDF sikeresen létrehozva: {PDF_OUTPUT_PATH}")
    print(f"✅ Másolat elmentve: {SKILL_PDF_PATH}")

def generate_html_doc():
    html_content = f"""<!DOCTYPE html>
<html lang="hu">
<head>
  <meta charset="UTF-8">
  <title>Election Tracker Skill Specifikáció</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      line-height: 1.6;
      color: #0f172a;
      background: #f8fafc;
      padding: 2rem;
      max-width: 900px;
      margin: 0 auto;
    }}
    .doc-card {{
      background: #ffffff;
      padding: 3rem;
      border-radius: 12px;
      border: 1px solid #e2e8f0;
      box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    }}
    h1 {{ color: #1e3a8a; border-bottom: 2px solid #3b82f6; padding-bottom: 0.5rem; }}
    h2 {{ color: #0f172a; margin-top: 2rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.3rem; }}
    table {{ width: 100%; border-collapse: collapse; margin: 1.5rem 0; }}
    th, td {{ border: 1px solid #cbd5e1; padding: 0.75rem 1rem; text-align: left; }}
    th {{ background: #f1f5f9; font-weight: 700; }}
    .badge {{ background: #eff6ff; color: #1d4ed8; padding: 0.2rem 0.6rem; border-radius: 4px; font-weight: 700; font-size: 0.85rem; }}
    pre {{ background: #0f172a; color: #f8fafc; padding: 1rem; border-radius: 8px; overflow-x: auto; font-size: 0.9rem; }}
    @media print {{
      body {{ background: #ffffff; padding: 0; }}
      .doc-card {{ border: none; box-shadow: none; padding: 0; }}
      .no-print {{ display: none; }}
    }}
  </style>
</head>
<body>
  <div class="no-print" style="margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;">
    <a href="ELECTION_TRACKER_SKILL.pdf" target="_blank" style="background: #2563eb; color: #ffffff; padding: 0.6rem 1.2rem; text-decoration: none; border-radius: 6px; font-weight: 700;">
      📥 Közvetlen PDF Megnyitása / Letöltése
    </a>
    <button onclick="window.print()" style="background: #0f172a; color: #ffffff; border: none; padding: 0.6rem 1.2rem; border-radius: 6px; font-weight: 700; cursor: pointer;">
      🖨️ Nyomtatás / Mentés PDF-ként
    </button>
  </div>
  <div class="doc-card">
    <h1>🗳️ Election Tracker Skill — Hivatalos Specifikáció</h1>
    <p><strong>Verzió:</strong> 2.0 (Nemzetközi Rendszer) | <strong>Elérési út:</strong> <code>.agent/skills/election-tracker</code></p>
    
    <h2>1. A Skill Áttekintése</h2>
    <p>Az <code>election-tracker</code> egy újrafelhasználható Antigravity AI képességcsomag, amely bármely célország választási rendszeréhez professzionális, interaktív és szigorúan hiteles adatvezérelt információs portált épít fel.</p>
    
    <h2>2. Nemzetközi Parlamenti Adatbázis</h2>
    <table>
      <thead>
        <tr><th>Ország</th><th>Törvényhozás</th><th>Összes Mandátum</th><th>Többségi Küszöb</th><th>Rendszer</th></tr>
      </thead>
      <tbody>
        <tr><td><strong>USA</strong></td><td>Szenátus / Képviselőház</td><td>100 / 435</td><td>51 / 218</td><td>Kétkamarás elnöki</td></tr>
        <tr><td><strong>Németország</strong></td><td>Bundestag</td><td>630</td><td>316</td><td>Arányos (5% bejutási küszöb)</td></tr>
        <tr><td><strong>Egyesült Királyság</strong></td><td>House of Commons</td><td>650</td><td>326</td><td>Westminsteri egyéni (FPTP)</td></tr>
        <tr><td><strong>Magyarország</strong></td><td>Országgyűlés</td><td>199</td><td>100 (133 kétharmad)</td><td>Vegyes (106 egyéni + 93 lista)</td></tr>
        <tr><td><strong>Franciaország</strong></td><td>Assemblée Nationale</td><td>577</td><td>289</td><td>Kétfordulós egyéni</td></tr>
      </tbody>
    </table>

    <h2>3. Hiteles Forrás Kritériumok</h2>
    <ul>
      <li><strong>Közvélemény-kutatók:</strong> Csak auditált módszertanú, A+, A vagy B+ minősítésű intézetek mérései engedélyezettek.</li>
      <li><strong>Média:</strong> Kizárólag nemzeti és nemzetközi Tier-1 hírügynökségek (AP, Reuters, DPA, BBC, Telex, 24.hu).</li>
    </ul>

    <h2>4. Parancssori Generálás</h2>
    <pre>python3 .agent/skills/election-tracker/scripts/scaffold_country.py --country hungary --output ~/Desktop/Valasztas-HU
python3 .agent/skills/election-tracker/scripts/scaffold_country.py --country germany --output ~/Desktop/Bundestag2025</pre>
  </div>
</body>
</html>
"""
    with open(HTML_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Nyomtatható HTML dokumentáció létrehozva: {HTML_OUTPUT_PATH}")

if __name__ == "__main__":
    generate_pdf()
    generate_html_doc()
