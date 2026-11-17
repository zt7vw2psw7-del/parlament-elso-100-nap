import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil

OUT_REPO = "/Users/berczizoltan/Documents/Egyetem/Politikatudomány MA - ELTE/Bibó/Sebők Miklós AI óra/Sebők Miklós AI kalandok/Parlament első 100 nap/abrak"
OUT_LEADANDO = "/Users/berczizoltan/Desktop/Berczi_Zoltan_Bibo_4blokk_leadando/abrak"
os.makedirs(OUT_REPO, exist_ok=True)
os.makedirs(OUT_LEADANDO, exist_ok=True)

DB_PATH = "/Users/berczizoltan/Documents/Egyetem/Politikatudomány MA - ELTE/Bibó/Sebők Miklós AI óra/Sebők Miklós AI kalandok/Parlament első 100 nap/parlament_100nap.db"
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

CAP_NAMES = {
    '1': 'Makrogazdaság', '2': 'Polgári jogok', '3': 'Egészségügy', '4': 'Mezőgazdaság',
    '5': 'Munkaügy', '6': 'Oktatás', '7': 'Környezetvédelem', '8': 'Energiaügy',
    '9': 'Bevándorlás', '10': 'Közlekedés', '12': 'Jog / Igazságszolg.', '13': 'Szociálpolitika',
    '14': 'Lakásügy', '15': 'Pénzügy / Keresk.', '16': 'Honvédelem', '17': 'Technológia / Média',
    '18': 'Külkereskedelem', '19': 'Külügyek / EU', '20': 'Kormányzati működés',
    '21': 'Földek / Vízügy', '23': 'Kultúra'
}

# =========================================================================
# 1. DIAGRAM: KULCSPOLITIKUSOK TEMATIKUS OSZLOPDIAGRAMJA (5 subplot)
# =========================================================================
politicians = [
    ('Magyar Péter', 'TISZA (2026)', '#3498db'),
    ('Dr. Gaudi-Nagy Tamás', 'Jobbik (2010)', '#9b59b6'),
    ('Rétvári Bence', 'KDNP (2010/2026)', '#e67e22'),
    ('Dr. Schiffer András', 'LMP (2010)', '#2ecc71'),
    ('Toroczkai László', 'Mi Hazánk (2026)', '#e74c3c')
]

fig, axes = plt.subplots(1, 5, figsize=(16, 4.5), dpi=180, sharey=False)

for idx, (name, party_label, color) in enumerate(politicians):
    ax = axes[idx]
    cur.execute('''
        SELECT sc.primary_topic_code, COUNT(*) as cnt
        FROM speech s
        JOIN speech_classification sc ON s.id = sc.speech_id
        WHERE s.speaker_name = ? AND s.word_count >= 200 AND s.is_procedural = 0
        GROUP BY sc.primary_topic_code
        ORDER BY cnt DESC
        LIMIT 5
    ''', (name,))
    rows = cur.fetchall()
    
    caps = [f"CAP {r[0]}\n{CAP_NAMES.get(r[0], r[0])[:12]}" for r in rows]
    counts = [r[1] for r in rows]
    
    bars = ax.bar(range(len(caps)), counts, color=color, alpha=0.85, edgecolor='black', linewidth=0.6)
    ax.set_title(f"{name}\n({party_label})", fontsize=9.5, fontweight='bold', pad=8)
    ax.set_xticks(range(len(caps)))
    ax.set_xticklabels(caps, rotation=35, ha='right', fontsize=7.5)
    ax.set_ylabel('Beszédek száma' if idx == 0 else '', fontsize=8.5)
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Értékek az oszlopok tetején
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.5, str(h), ha='center', va='bottom', fontsize=8, fontweight='bold')

fig.suptitle('Kulcspolitikusok Felszólalásainak Tematikus Megoszlása (Top 5 téma személyenként)', fontsize=12, fontweight='bold', y=1.03)
plt.tight_layout()

file_pol = os.path.join(OUT_REPO, "abra_politikusok_oszlopdiagram.png")
plt.savefig(file_pol, bbox_inches='tight')
shutil.copy2(file_pol, os.path.join(OUT_LEADANDO, "abra_politikusok_oszlopdiagram.png"))
plt.close()
print("✅ Politikusok oszlopdiagram elmentve.")

# =========================================================================
# 2. DIAGRAM: FRAKCIÓK SZERINTI TEMATIKUS OSZLOPDIAGRAMOK (2x3 panel)
# =========================================================================
parties = [
    ('TISZA', 'TISZA Frakció (2026)', '#2980b9'),
    ('FIDESZ', 'Fidesz Frakció', '#d35400'),
    ('KDNP', 'KDNP Frakció', '#f39c12'),
    ('MI_HAZANK', 'Mi Hazánk Frakció (2026)', '#c0392b'),
    ('JOBBIK', 'Jobbik Frakció (2010)', '#8e44ad'),
    ('MSZP', 'MSZP Frakció (2010)', '#c0392b'),
]

fig2, axes2 = plt.subplots(2, 3, figsize=(15, 7.5), dpi=180)
axes_flat = axes2.flatten()

for idx, (pcode, plabel, pcol) in enumerate(parties):
    ax = axes_flat[idx]
    cur.execute('''
        SELECT sc.primary_topic_code, COUNT(*) as cnt
        FROM speech s
        JOIN speech_classification sc ON s.id = sc.speech_id
        JOIN parliamentary_group pg ON s.group_id = pg.id
        WHERE pg.party_code = ? AND s.word_count >= 200 AND s.is_procedural = 0
        GROUP BY sc.primary_topic_code
        ORDER BY cnt DESC
        LIMIT 6
    ''', (pcode,))
    rows = cur.fetchall()
    
    labels = [f"CAP {r[0]}: {CAP_NAMES.get(r[0], r[0])[:15]}" for r in rows]
    counts = [r[1] for r in rows]
    
    y_pos = np.arange(len(labels))
    bars = ax.barh(y_pos, counts, color=pcol, alpha=0.8, edgecolor='black', linewidth=0.5, height=0.65)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_title(plabel, fontsize=9.5, fontweight='bold', pad=6)
    ax.set_xlabel('Felszólalások (db)', fontsize=8)
    ax.grid(axis='x', linestyle='--', alpha=0.4)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    total_p = sum(counts)
    for bar in bars:
        w = bar.get_width()
        pct = (w / total_p) * 100
        ax.text(w + 1, bar.get_y() + bar.get_height()/2, f"{int(w)} ({pct:.0f}%)", va='center', fontsize=7.5)

fig2.suptitle('Parlamenti Frakciók Szakpolitikai Súlypontjai (Top 6 téma frakciónként)', fontsize=12, fontweight='bold', y=0.99)
plt.tight_layout()

file_frakc = os.path.join(OUT_REPO, "abra_frakciok_oszlopdiagram.png")
plt.savefig(file_frakc, bbox_inches='tight')
shutil.copy2(file_frakc, os.path.join(OUT_LEADANDO, "abra_frakciok_oszlopdiagram.png"))
plt.close()
print("✅ Frakciók oszlopdiagram elmentve.")

conn.close()
