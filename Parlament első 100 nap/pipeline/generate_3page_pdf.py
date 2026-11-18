#!/usr/bin/env python3
"""
3 oldalas tudományos parlamenti elemzés PDF generálása (fpdf2 alapon).
Szigorúan 3 oldal:
1. oldal: Cím, Bevezetés, Korpusz, Módszertan, 1. táblázat (CAP eloszlás)
2. oldal: Eredmények, 1. ábra (CAP főkategóriák), 2. ábra (2010 vs 2026 összehasonlítás)
3. oldal: Viták és agendaváltások, 2. táblázat (Agendaváltások), Értelmezés, 3. ábra (CAP 20 összetétele)
"""

import os
import sys
from fpdf import FPDF

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(BASE_DIR, "abrak")
OUT_PDF = os.path.join(BASE_DIR, "parlament_100nap_elemzes_3oldal.pdf")

pdf = FPDF(orientation="P", unit="mm", format="A4")
pdf.set_auto_page_break(auto=False)
pdf.set_margins(left=18, top=14, right=18)

FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_B_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_I_PATH = "/System/Library/Fonts/Supplemental/Arial Italic.ttf"

pdf.add_font("Arial", "", FONT_PATH)
pdf.add_font("Arial", "B", FONT_B_PATH)
pdf.add_font("Arial", "I", FONT_I_PATH)

# ==========================================
# 1. OLDAL
# ==========================================
pdf.add_page()

pdf.set_font("Arial", "B", 13.5)
pdf.set_text_color(26, 58, 92)
pdf.cell(0, 6.5, "Parlamenti agendabeállítás az első 100 napban:", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.cell(0, 6.5, "A 2010-es (Fidesz–KDNP) és 2026-os (TISZA) kormányváltás összehasonlító elemzése", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.ln(1)

pdf.set_font("Arial", "I", 8)
pdf.set_text_color(90, 90, 90)
pdf.cell(0, 4.5, "Szerző: Bérczi Zoltán  |  Kurzusvezető: Sebők Miklós  |  ELTE Bibó István Szakkollégium  |  2026. november", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.set_draw_color(26, 58, 92)
pdf.set_line_width(0.4)
pdf.line(18, pdf.get_y()+1, 192, pdf.get_y()+1)
pdf.ln(3)

# 1. Bevezetés
pdf.set_font("Arial", "B", 9.5)
pdf.set_text_color(26, 58, 92)
pdf.cell(0, 4.8, "1. Bevezetés és kutatási kérdés", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Arial", "", 8.2)
pdf.set_text_color(20, 20, 20)
intro_text = (
    "A demokratikus kormányváltásokat követő első száz nap kitüntetett jelentőségű a politikatudományban és az agendakutatásban: "
    "ebben az időszakban rajzolódik ki legtisztábban az új kabinet kormányzati logikája és szakpolitikai prioritásrendszere. "
    "Kutatásunk célja a 2010-es kétharmados Fidesz–KDNP fordulat és a 2026-os TISZA-kormányzás első 100 parlamenti napjának "
    "összehasonlító agendavizsgálata. Arra a kérdésre keressük a választ, hogy a parlamentáris nyilvánosságban az intézményi reformok "
    "mellett milyen szakpolitikai súlypontok domináltak, és az új kormányok hogyan strukturálták törvényhozási vitáikat."
)
pdf.multi_cell(0, 3.8, intro_text)
pdf.ln(1.5)

# 2. Adatbázis
pdf.set_font("Arial", "B", 9.5)
pdf.set_text_color(26, 58, 92)
pdf.cell(0, 4.8, "2. Adatbázis és korpusz (ParlLawSpeech standard)", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Arial", "", 8.2)
pdf.set_text_color(20, 20, 20)
data_text = (
    "A vizsgálati korpusz az Országgyűlés hivatalos naplóiból kinyert, normalizált relációs SQLite adatbázisra épül (parlament_100nap.db). "
    "Az adatbázis a nemzetközi ParlLawSpeech adatmodellnek megfelelően kapcsolja össze a képviselőket (n=492), parlamenti pártokat, "
    "üléseket, felszólalásokat és törvényjavaslatokat (n=127). A korpusz két 100 napos szakaszt ölel fel: a 2010-es ciklust "
    "(2010. május 14. – augusztus 22.) és a 2026-os ciklust (2026. május 9. – augusztus 17.). "
    "Az érdemi szakpolitikai viták tisztaságának biztosítására kiszűrtük a technikai elnöki levezetéseket, szavaztatásokat, ügyrendi "
    "hozzászólásokat és mandátumigazolási vitákat (összesen n=186 procedurális eset), így az érdemi elemzési minta 3 687 felszólalást "
    "tartalmaz (2010: 2 200 db, 2026: 1 487 db; átlagosan 4 350 karakter/beszéd)."
)
pdf.multi_cell(0, 3.8, data_text)
pdf.ln(1.5)

# 3. Módszertan
pdf.set_font("Arial", "B", 9.5)
pdf.set_text_color(26, 58, 92)
pdf.cell(0, 4.8, "3. Módszertan: Tartalmi szövegalapú CAP kódolás és eljárási szűrés", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Arial", "", 8.2)
pdf.set_text_color(20, 20, 20)
method_text = (
    "A felszólalások tematikus besorolása a Comparative Agendas Project (CAP) 21 főkategóriáján alapul. "
    "A besorolás során a törvényeket és felszólalásokat a teljes szövegük (full_text) tartalomelemzése alapján osztályoztuk. "
    "Az önkormányzati feladatokat a CAP standardnak megfelelően a CAP 14 (Településfejlesztés) alá rendeltük, a gazdasági "
    "akcióterveket a CAP 1-hez, míg a technikai eljárási és mandátumigazolási megnyilvánulásokat procedurálisan félretettük. "
    "Ennek eredményeként a korábbi mesterségesen magas CAP 20 arány 19,9%-ra (732 db) normalizálódott, valós szakpolitikai egyensúlyt teremtve."
)
pdf.multi_cell(0, 3.8, method_text)
pdf.ln(2)

# 1. TÁBLÁZAT
pdf.set_font("Arial", "B", 8.2)
pdf.set_text_color(26, 58, 92)
pdf.cell(0, 4.2, "1. táblázat: A legfőbb CAP témakategóriák megoszlása tartalmi szövegelemzés alapján (N = 3 687)", new_x="LMARGIN", new_y="NEXT")

col_widths = [14, 55, 20, 18, 23, 23, 21]
headers = ["CAP", "Szakpolitikai témakör", "Összes (db)", "Arány (%)", "2010 (db)", "2026 (db)", "Prioritás"]
pdf.set_font("Arial", "B", 7.5)
pdf.set_fill_color(26, 58, 92)
pdf.set_text_color(255, 255, 255)
for w, h in zip(col_widths, headers):
    pdf.cell(w, 4.8, h, border=1, align="C", fill=True)
pdf.ln()

table_data = [
    ("20", "Alkotmányosság, kormányzati szerkezet", "732", "19,9%", "421", "311", "Mindkettő"),
    ("12", "Jog, igazságszolgáltatás, közbiztonság", "419", "11,4%", "250", "169", "2010 > 2026"),
    ("1", "Makrogazdaság, költségvetés, adóügyek", "412", "11,2%", "297", "115", "2010 fókusz (2,6x)"),
    ("15", "Belkereskedelem, pénzügy, bankok", "271", "7,4%", "207", "64", "2010 fókusz (3,2x)"),
    ("14", "Településfejlesztés, önkormányzatok", "267", "7,2%", "174", "93", "2010 > 2026"),
    ("6", "Oktatás és felsőoktatás", "267", "7,2%", "152", "115", "Kiegyensúlyozott"),
    ("4", "Mezőgazdaság és agrárpolitika", "190", "5,2%", "86", "104", "2026 fókusz"),
    ("3", "Egészségügy és betegellátás", "172", "4,7%", "56", "116", "2026 fókusz (2,1x)"),
    ("17", "Technológia, média, távközlés", "143", "3,9%", "104", "39", "2010 fókusz (2,7x)"),
    ("13", "Szociálpolitika és jólét", "142", "3,9%", "95", "47", "2010 fókusz (2,0x)"),
    ("19", "Nemzetközi kapcsolatok, külügyek / EU", "106", "2,9%", "25", "81", "2026 fókusz (3,2x)"),
    ("10", "Közlekedés és infrastruktúra", "97", "2,6%", "34", "63", "2026 fókusz (1,9x)"),
]

pdf.set_font("Arial", "", 7.3)
pdf.set_text_color(20, 20, 20)
for idx, row in enumerate(table_data):
    fill = (idx % 2 == 1)
    pdf.set_fill_color(235, 242, 250) if fill else pdf.set_fill_color(255, 255, 255)
    pdf.cell(col_widths[0], 4.2, row[0], border=1, align="C", fill=fill)
    pdf.cell(col_widths[1], 4.2, row[1], border=1, align="L", fill=fill)
    pdf.cell(col_widths[2], 4.2, row[2], border=1, align="C", fill=fill)
    pdf.cell(col_widths[3], 4.2, row[3], border=1, align="C", fill=fill)
    pdf.cell(col_widths[4], 4.2, row[4], border=1, align="C", fill=fill)
    pdf.cell(col_widths[5], 4.2, row[5], border=1, align="C", fill=fill)
    pdf.cell(col_widths[6], 4.2, row[6], border=1, align="C", fill=fill)
    pdf.ln()

# ==========================================
# 2. OLDAL
# ==========================================
pdf.add_page()

pdf.set_font("Arial", "B", 9.5)
pdf.set_text_color(26, 58, 92)
pdf.cell(0, 4.8, "4. Eredmények és összehasonlító agendavizsgálat", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Arial", "", 8.2)
pdf.set_text_color(20, 20, 20)
res_text = (
    "A tartalmi szövegelemzés és az eljárási szűrés eredményeként a parlamenti viták valós szakpolitikai súlypontjai rajzolódnak ki. "
    "A korábbi technikai és ügyrendi torzítások feloldása után a CAP 20 (kormányzati struktúra, alkotmányozás) 19,9%-ra állt be (732 db), "
    "míg a szakpolitikai területek összesített aránya eléri a 80,1%-ot. "
    "A törvényhozási agenda gerincét a jogi elszámoltatás és igazságszolgáltatás (CAP 12, 11,4%), a makrogazdasági adó- és költségvetési ügyek "
    "(CAP 1, 11,2%), a pénzügyi szektor szabályozása (CAP 15, 7,4%), valamint az önkormányzati reformok (CAP 14, 7,2%) adják."
)
pdf.multi_cell(0, 3.8, res_text)
pdf.ln(1.5)

img1 = os.path.join(IMG_DIR, "abra1_cap_eloszlas.png")
if os.path.exists(img1):
    pdf.image(img1, x=22, y=pdf.get_y(), w=150)
    pdf.set_y(pdf.get_y() + 82)

pdf.set_font("Arial", "I", 7.5)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 3.5, "1. ábra: A parlamenti felszólalások CAP témák szerinti megoszlása a tartalmi kódolás alapján (N = 3 687)", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.ln(2.5)

img2 = os.path.join(IMG_DIR, "abra2_2010vs2026.png")
if os.path.exists(img2):
    pdf.image(img2, x=22, y=pdf.get_y(), w=150)
    pdf.set_y(pdf.get_y() + 82)

pdf.set_font("Arial", "I", 7.5)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 3.5, "2. ábra: Szakpolitikai súlypontok összevetése: 2010 (Fidesz–KDNP) vs. 2026 (TISZA)", new_x="LMARGIN", new_y="NEXT", align="C")

# ==========================================
# 3. OLDAL
# ==========================================
pdf.add_page()

pdf.set_font("Arial", "B", 9.5)
pdf.set_text_color(26, 58, 92)
pdf.cell(0, 4.8, "5. Főbb agendaváltási minták és politikatudományi tanulságok", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Arial", "", 8.2)
pdf.set_text_color(20, 20, 20)
disc_text = (
    "Az adatok megerősítik, hogy az agendabeállítás pontosan képezi le a két korszakváltás társadalmi és gazdasági kontextusát. "
    "2010 a globális pénzügyi válság utáni fiskális fegyelem és a munkaalapú gazdaság megteremtésének jegyében telt, "
    "míg 2026-ban a tizennégy év után megörökölt közszolgáltatási lemaradás (kórházi várólisták, vasúti krízis) "
    "és a befagyasztott uniós források (RRF) hazahozatala alakította a parlamenti viták struktúráját."
)
pdf.multi_cell(0, 3.8, disc_text)
pdf.ln(1.5)

pdf.set_font("Arial", "B", 8.2)
pdf.set_text_color(26, 58, 92)
pdf.cell(0, 4.2, "2. táblázat: A legmarkánsabb szakpolitikai agendaváltások a két kormányváltás között", new_x="LMARGIN", new_y="NEXT")

col_w2 = [48, 25, 25, 26, 50]
headers2 = ["Szakpolitika (CAP)", "2010 (db)", "2026 (db)", "Változás", "Főbb tartalmi fókusz"]
pdf.set_font("Arial", "B", 7.5)
pdf.set_fill_color(26, 58, 92)
pdf.set_text_color(255, 255, 255)
for w, h in zip(col_w2, headers2):
    pdf.cell(w, 4.8, h, border=1, align="C", fill=True)
pdf.ln()

table_data2 = [
    ("Külügyek és EU (CAP 19)", "25", "81", "+224% (3,2x)", "Uniós források, RRF jogállamisági feltételek"),
    ("Egészségügy (CAP 3)", "56", "116", "+107% (2,1x)", "Kórházi állapotok, várólisták, orvosbérek"),
    ("Energiaügy (CAP 8)", "23", "56", "+143% (2,4x)", "Helyreállítási Terv energetikai reformjai"),
    ("Közlekedés (CAP 10)", "34", "63", "+85% (1,9x)", "MÁV infrastruktúra, vonatkésések"),
    ("Makrogazdaság (CAP 1)", "297", "115", "-61%", "29 pontos gazdasági akcióterv (2010)"),
    ("Pénzügy / kereskedelem (CAP 15)", "207", "64", "-69%", "Bankadó, devizahitelek korlátozása (2010)"),
    ("Település / Önkorm. (CAP 14)", "174", "93", "-47%", "Önkormányzati rendszer átalakítása (2010)"),
]

pdf.set_font("Arial", "", 7.3)
pdf.set_text_color(20, 20, 20)
for idx, row in enumerate(table_data2):
    fill = (idx % 2 == 1)
    pdf.set_fill_color(235, 242, 250) if fill else pdf.set_fill_color(255, 255, 255)
    pdf.cell(col_w2[0], 4.2, row[0], border=1, align="L", fill=fill)
    pdf.cell(col_w2[1], 4.2, row[1], border=1, align="C", fill=fill)
    pdf.cell(col_w2[2], 4.2, row[2], border=1, align="C", fill=fill)
    pdf.cell(col_w2[3], 4.2, row[3], border=1, align="C", fill=fill)
    pdf.cell(col_w2[4], 4.2, row[4], border=1, align="L", fill=fill)
    pdf.ln()
pdf.ln(1.5)

pdf.set_font("Arial", "B", 9.5)
pdf.set_text_color(26, 58, 92)
pdf.cell(0, 4.8, "6. Módszertani megbízhatóság és validáció", new_x="LMARGIN", new_y="NEXT")

curr_y = pdf.get_y()
img3 = os.path.join(IMG_DIR, "abra3_cap20_osszetevel.png")
if os.path.exists(img3):
    pdf.image(img3, x=136, y=curr_y, w=54)

pdf.set_font("Arial", "", 8.0)
pdf.set_text_color(20, 20, 20)
limit_text = (
    "A vizsgálat során a tanári visszajelzések alapján a formális címalapú osztályozást felváltotta "
    "a teljes szöveges tartalomelemzés (full-text content scoring). "
    "A 3. ábra szemlélteti, hogy a korrekció és az eljárási szűrés révén a CAP 20 aránya 19,9%-ra (732 db) mérséklődött, "
    "míg a szakpolitikai sokféleség nőtt (21 aktív CAP téma). "
    "A mesterséges intelligencia (Gemini 2.5 Flash / Pro) alkalmazása a kódolási szabályok szisztematikus betartását szolgálta, "
    "míg az eljárási szűrés és a döntési határok felügyelete teljes egészében kutatói kontroll alatt állt (Human-in-the-Loop)."
)
# Leave space for side image
pdf.set_x(18)
for line in pdf.multi_cell(115, 3.8, limit_text, dry_run=True, output="LINES"):
    pdf.set_x(18)
    pdf.cell(115, 3.8, line, new_x="LMARGIN", new_y="NEXT")

pdf.set_y(curr_y + 44)
pdf.set_font("Arial", "I", 7.2)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 3.2, "3. ábra: A CAP 20 konszolidációja a tartalmi és eljárási finomhangolás után", new_x="LMARGIN", new_y="NEXT", align="R")
pdf.ln(1.5)

# 7. Összegzés
pdf.set_font("Arial", "B", 9.5)
pdf.set_text_color(26, 58, 92)
pdf.cell(0, 4.8, "7. Összegzés", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Arial", "", 8.2)
pdf.set_text_color(20, 20, 20)
concl_text = (
    "A két kormányváltás első 100 napjának agendavizsgálata rámutat: míg a 2010-es Fidesz–KDNP kormányzat a válságkezelést "
    "központosított gazdasági és intézményi törvényhozási rohammal (CAP 1, CAP 12, CAP 15) oldotta meg, "
    "addig a 2026-os TISZA-kormány a társadalmi szolgáltatások megerősítésére (egészségügy, oktatás, közlekedés) "
    "és a nemzetközi/európai kapcsolatok (CAP 19) helyreállítására helyezte a hangsúlyt. "
    "Az eljárásrendi felszólalások szűrése és a tartalmi kódolás révén mindkét időszakban tiszta, empirikusan megalapozott "
    "szakpolitikai preferenciarangsor mutatható ki."
)
pdf.multi_cell(0, 3.8, concl_text)

pdf.output(OUT_PDF)
print(f"✅ SIKER: 3 oldalas PDF legenerálva ide: {OUT_PDF}")
