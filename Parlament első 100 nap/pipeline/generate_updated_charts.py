import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os
import shutil

REPO_DIR = "/Users/berczizoltan/Documents/Egyetem/Politikatudomány MA - ELTE/Bibó/Sebők Miklós AI óra/Sebők Miklós AI kalandok/Parlament első 100 nap"
IMG_REPO = os.path.join(REPO_DIR, "abrak")
IMG_LEADANDO = "/Users/berczizoltan/Desktop/Berczi_Zoltan_Bibo_4blokk_leadando/abrak"
os.makedirs(IMG_REPO, exist_ok=True)
os.makedirs(IMG_LEADANDO, exist_ok=True)

DB_PATH = os.path.join(REPO_DIR, "parlament_100nap.db")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

CAP_NAMES = {
    1: "Makrogazdaság", 2: "Polgári jogok", 3: "Egészségügy", 4: "Mezőgazdaság",
    5: "Munkaügy", 6: "Oktatás", 7: "Környezetvédelem", 8: "Energiaügy",
    9: "Bevándorlás", 10: "Közlekedés", 12: "Jog / Közbiztonság",
    13: "Szociálpolitika", 14: "Település / Önkorm.", 15: "Pénzügy / Keresk.",
    16: "Honvédelem", 17: "Technológia / Média", 18: "Külkereskedelem",
    19: "Külügyek / EU", 20: "Alkotmány / Kormányzat", 21: "Földek / Vízügy", 23: "Kultúra"
}

# 1. Lekérjük a pontos új megoszlást
cur.execute('''
    SELECT CAST(sc.primary_topic_code AS INTEGER) as cap,
           COUNT(*) as cnt,
           SUM(CASE WHEN s.period_id='2010' THEN 1 ELSE 0 END) as y2010,
           SUM(CASE WHEN s.period_id='2026' THEN 1 ELSE 0 END) as y2026
    FROM speech s
    JOIN speech_classification sc ON s.id = sc.speech_id
    WHERE s.word_count >= 200 AND s.is_procedural = 0
    GROUP BY cap
    ORDER BY cnt DESC
''')
data = cur.fetchall()
total = sum(d[1] for d in data)

# --- 1. ÁBRA: Vízszintes bar chart (Összesített CAP megoszlás) ---
top12 = data[:12]
caps = [d[0] for d in top12]
counts = [d[1] for d in top12]
labels = [f"CAP {c}\n{CAP_NAMES.get(c, str(c))}" for c in caps]
pcts = [c/total*100 for c in counts]

fig, ax = plt.subplots(figsize=(8, 5), dpi=180)
colors = ['#c0392b' if c==20 else '#2980b9' for c in caps]
bars = ax.barh(range(len(caps)), pcts, color=colors, edgecolor='white', height=0.65)
ax.set_yticks(range(len(caps)))
ax.set_yticklabels(labels, fontsize=8.5)
ax.invert_yaxis()
ax.set_xlabel('Az érdemi felszólalások %-a', fontsize=9)
ax.set_title('1. ábra – CAP témakategóriák megoszlása\n(3 813 érdemi felszólalás, tartalmi szövegelemzés alapján)', fontsize=10, fontweight='bold')
for bar, pct, cnt in zip(bars, pcts, counts):
    ax.text(bar.get_width()+0.2, bar.get_y()+bar.get_height()/2, f'{pct:.1f}% (n={cnt})', va='center', fontsize=7.5)
ax.set_xlim(0, 26)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
red_patch = mpatches.Patch(color='#c0392b', label='CAP 20 – Alkotmány / Kormányzati szerkezet (21,0%)')
blue_patch = mpatches.Patch(color='#2980b9', label='Szakpolitikai kategóriák (79,0%)')
ax.legend(handles=[red_patch, blue_patch], fontsize=8, loc='lower right')
plt.tight_layout()
p1 = os.path.join(IMG_REPO, 'abra1_cap_eloszlas.png')
plt.savefig(p1, bbox_inches='tight')
shutil.copy2(p1, os.path.join(IMG_LEADANDO, 'abra1_cap_eloszlas.png'))
plt.close()
print("✅ 1. ábra kész")

# --- 2. ÁBRA: 2010 vs 2026 összehasonlító oszlopdiagram ---
compare = [d for d in data if (d[2]+d[3]) >= 80][:10]
caps2 = [c[0] for c in compare]
v2010 = [c[2] for c in compare]
v2026 = [c[3] for c in compare]
labels2 = [f"CAP {c}\n{CAP_NAMES.get(c, str(c))[:12]}" for c in caps2]

x = np.arange(len(caps2))
width = 0.38
fig, ax = plt.subplots(figsize=(9.5, 4.8), dpi=180)
b1 = ax.bar(x - width/2, v2010, width, label='2010 (Fidesz–KDNP)', color='#2c3e50', alpha=0.85)
b2 = ax.bar(x + width/2, v2026, width, label='2026 (TISZA)', color='#e67e22', alpha=0.85)
ax.set_xticks(x)
ax.set_xticklabels(labels2, fontsize=8)
ax.set_ylabel('Felszólalások száma', fontsize=9)
ax.set_title('2. ábra – Szakpolitikai fókusz: 2010 vs. 2026\n(Top szakpolitikák a teljes szövegelemzés alapján)', fontsize=10, fontweight='bold')
ax.legend(fontsize=9)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
for bar in [*b1, *b2]:
    h = bar.get_height()
    if h > 0:
        ax.text(bar.get_x()+bar.get_width()/2, h+3, str(h), ha='center', fontsize=7.5)
plt.tight_layout()
p2 = os.path.join(IMG_REPO, 'abra2_2010vs2026.png')
plt.savefig(p2, bbox_inches='tight')
shutil.copy2(p2, os.path.join(IMG_LEADANDO, 'abra2_2010vs2026.png'))
plt.close()
print("✅ 2. ábra kész")

# --- 3. ÁBRA: Kördiagram a CAP 20 redukciójáról ---
fig, ax = plt.subplots(figsize=(5.5, 4), dpi=180)
sizes = [802, 3011]
labels3 = [f'CAP 20 Alkotmányozás\n(n=802, 21.0%)', f'Szakpolitikák\n(n=3011, 79.0%)']
colors3 = ['#e74c3c', '#2980b9']
explode = (0.05, 0)
wedges, texts, autotexts = ax.pie(sizes, labels=labels3, colors=colors3, explode=explode,
                                  autopct='%1.1f%%', startangle=140, textprops={'fontsize': 8.5})
ax.set_title('3. ábra – A CAP 20 aránya a finomhangolás után\n(Intézményi vita vs. valós szakpolitikák)', fontsize=9.5, fontweight='bold')
plt.tight_layout()
p3 = os.path.join(IMG_REPO, 'abra3_cap20_osszetevel.png')
plt.savefig(p3, bbox_inches='tight')
shutil.copy2(p3, os.path.join(IMG_LEADANDO, 'abra3_cap20_osszetevel.png'))
plt.close()
print("✅ 3. ábra kész")

conn.close()
print("Minden tanulmánybeli ábra sikeresen frissítve!")
