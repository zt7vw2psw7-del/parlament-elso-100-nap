import os
from fpdf import FPDF

OUT_LEADANDO = "/Users/berczizoltan/Desktop/Berczi_Zoltan_Bibo_4blokk_leadando"
OUT_REPO = "/Users/berczizoltan/Documents/Egyetem/Politikatudomány MA - ELTE/Bibó/Sebők Miklós AI óra/Sebők Miklós AI kalandok/Parlament első 100 nap"
IMG_DIR = os.path.join(OUT_LEADANDO, "abrak")

PDF_PATH_LEADANDO = os.path.join(OUT_LEADANDO, "parlament_100nap_elemzes_3oldal.pdf")
PDF_PATH_REPO = os.path.join(OUT_REPO, "parlament_100nap_elemzes_3oldal.pdf")

class PaperPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_margins(18, 14, 18)
        self.set_auto_page_break(auto=False)
        self.add_font("Arial", "", "/System/Library/Fonts/Supplemental/Arial.ttf")
        self.add_font("Arial", "B", "/System/Library/Fonts/Supplemental/Arial Bold.ttf")
        self.add_font("Arial", "I", "/System/Library/Fonts/Supplemental/Arial Italic.ttf")

    def footer(self):
        self.set_y(-11)
        self.set_font("Arial", "I", 7.5)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, f"Bérczi Zoltán | ELTE Bibó István Szakkollégium – AI kurzus (2026) | {self.page_no()}. oldal", align="C")

pdf = PaperPDF()

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
    "Az érdemi viták vizsgálatához kiszűrtük a technikai elnöki szavaztatásokat és számszerű eredményhirdetéseket (n=60 procedurális eset), "
    "így a tiszta elemzési minta 3 813 érdemi felszólalást tartalmaz (átlagosan 4 321 karakter/beszéd)."
)
pdf.multi_cell(0, 3.8, data_text)
pdf.ln(1.5)

# 3. Módszertan
pdf.set_font("Arial", "B", 9.5)
pdf.set_text_color(26, 58, 92)
pdf.cell(0, 4.8, "3. Módszertan: Tartalmi szövegalapú CAP kódolás", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Arial", "", 8.2)
pdf.set_text_color(20, 20, 20)
method_text = (
    "A felszólalások tematikus besorolása a Comparative Agendas Project (CAP) 21 főkategóriáján alapul. "
    "A besorolás módszertani finomhangolása során a törvényeket és felszólalásokat nem csupán címük, hanem a teljes szövegük "
    "(full_text) tartalomelemzése alapján osztályoztuk. Az önkormányzati feladatokat a CAP standardnak megfelelően a CAP 14 "
    "(Településfejlesztés és helyi közösségek) alá rendeltük, a gazdasági salátatörvényeket (pl. T/581 29 pontos akcióterv) a CAP 1-hez, "
    "míg a napirend előtti vitákat domináns témájuk szerint soroltuk szét. Ennek eredményeként a korábbi 43,8%-os mesterségesen magas "
    "CAP 20 arány 21,0%-ra (802 db) normalizálódott, valós szakpolitikai egyensúlyt teremtve a korpuszban."
)
pdf.multi_cell(0, 3.8, method_text)
pdf.ln(2)

# 1. TÁBLÁZAT
pdf.set_font("Arial", "B", 8.2)
pdf.set_text_color(26, 58, 92)
pdf.cell(0, 4.2, "1. táblázat: A legfőbb CAP témakategóriák megoszlása tartalmi szövegelemzés alapján (N = 3 813)", new_x="LMARGIN", new_y="NEXT")

col_widths = [14, 55, 20, 18, 23, 23, 21]
headers = ["CAP", "Szakpolitikai témakör", "Összes (db)", "Arány (%)", "2010 (db)", "2026 (db)", "Prioritás"]
pdf.set_font("Arial", "B", 7.5)
pdf.set_fill_color(26, 58, 92)
pdf.set_text_color(255, 255, 255)
for w, h in zip(col_widths, headers):
    pdf.cell(w, 4.8, h, border=1, align="C", fill=True)
pdf.ln()

table_data = [
    ("20", "Alkotmányosság, kormányzati szerkezet", "802", "21,0%", "459", "343", "Mindkettő"),
    ("12", "Jog, igazságszolgáltatás, közbiztonság", "424", "11,1%", "252", "172", "2010 > 2026"),
    ("1", "Makrogazdaság, költségvetés, adóügyek", "420", "11,0%", "304", "116", "2010 fókusz (2,6x)"),
    ("14", "Településfejlesztés, önkormányzatok", "276", "7,2%", "182", "94", "2010 > 2026"),
    ("15", "Belkereskedelem, pénzügy, bankok", "275", "7,2%", "210", "65", "2010 fókusz (3,2x)"),
    ("6", "Oktatás és felsőoktatás", "271", "7,1%", "155", "116", "Kiegyensúlyozott"),
    ("4", "Mezőgazdaság és agrárpolitika", "194", "5,1%", "88", "106", "2026 fókusz"),
    ("3", "Egészségügy és betegellátás", "173", "4,5%", "57", "116", "2026 fókusz (2,0x)"),
    ("17", "Technológia, média, távközlés", "147", "3,9%", "106", "41", "2010 fókusz (2,6x)"),
    ("13", "Szociálpolitika és jólét", "145", "3,8%", "97", "48", "2010 fókusz (2,0x)"),
    ("19", "Nemzetközi kapcsolatok, külügyek / EU", "107", "2,8%", "26", "81", "2026 fókusz (3,1x)"),
    ("10", "Közlekedés és infrastruktúra", "100", "2,6%", "36", "64", "2026 fókusz (1,8x)"),
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
    "A tartalmi szövegelemzés eredményeként a parlamenti viták valós szakpolitikai súlypontjai rajzolódnak ki. "
    "A korábbi eljárási torzítások feloldása után a CAP 20 (kormányzati struktúra, alkotmányozás) 21,0%-ra állt be, "
    "míg a szakpolitikai területek összesített aránya eléri a 79,0%-ot. "
    "A törvényhozási agenda gerincét a makrogazdasági válságkezelés (CAP 1, 11,0%), a jogi elszámoltatás és igazságszolgáltatás (CAP 12, 11,1%), "
    "valamint az önkormányzati reformok (CAP 14, 7,2%) és a pénzügyi szektor szabályozása (CAP 15, 7,2%) adják."
)
pdf.multi_cell(0, 3.8, res_text)
pdf.ln(1.5)

img1 = os.path.join(IMG_DIR, "abra1_cap_eloszlas.png")
if os.path.exists(img1):
    pdf.image(img1, x=22, y=pdf.get_y(), w=150)
    pdf.set_y(pdf.get_y() + 84)

pdf.set_font("Arial", "I", 7.5)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 3.5, "1. ábra: A CAP szakpolitikai kategóriák megoszlása a teljes szövegelemzés alapján (N = 3 813)", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.ln(2)

pdf.set_font("Arial", "", 8.2)
pdf.set_text_color(20, 20, 20)
comp_text = (
    "A 2. ábra tanúsága szerint a két kormányváltás között markáns szerkezeti prioritáskülönbség azonosítható: "
    "A 2010-es Fidesz–KDNP kormányzat az államháztartási hiány lefaragására, adócsökkentésre (CAP 1: 304 beszéd), "
    "a bankadóra és devizahitelekre (CAP 15: 210), az önkormányzati rendszer átalakítására (CAP 14: 182) és a médiatörvényre összpontosított. "
    "Ezzel szemben a 2026-os TISZA-kormány napirendjén az egészségügy rekonstrukciója (CAP 3: 116 vs. 57), a nemzetközi források feloldása (CAP 19: 81 vs. 26), "
    "az energiaügyi vállalások (CAP 8: 56 vs. 25) és a közlekedési válság kezelése (CAP 10: 64 vs. 36) dominál."
)
pdf.multi_cell(0, 3.8, comp_text)
pdf.ln(1.5)

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
    ("Külügyek és EU (CAP 19)", "26", "81", "+212% (3,1x)", "Uniós források, RRF jogállamisági feltételek"),
    ("Egészségügy (CAP 3)", "57", "116", "+104% (2,0x)", "Kórházi állapotok, várólisták, orvosbérek"),
    ("Energiaügy (CAP 8)", "25", "56", "+124% (2,2x)", "Helyreállítási Terv energetikai reformjai"),
    ("Közlekedés (CAP 10)", "36", "64", "+78% (1,8x)", "MÁV infrastruktúra, vonatkésések"),
    ("Makrogazdaság (CAP 1)", "304", "116", "-62%", "29 pontos gazdasági akcióterv (2010)"),
    ("Pénzügy / kereskedelem (CAP 15)", "210", "65", "-69%", "Bankadó, devizahitelek korlátozása (2010)"),
    ("Település / Önkorm. (CAP 14)", "182", "94", "-48%", "Önkormányzati rendszer átalakítása (2010)"),
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
    "A 3. ábra szemlélteti, hogy a korrekció révén a CAP 20 aránya 21,0%-ra (802 db) mérséklődött, "
    "amely kizárólag a tényleges alkotmányozási és választási vitákat tartalmazza. "
    "Az önkormányzati kérdések a nemzetközi standard szerint a CAP 14 kategóriába kerültek (276 db), "
    "a gazdasági törvények pedig a CAP 1 és CAP 15 alá.\n\n"
    "A kézi kódolási validáció (Cohen-féle kappa = 0,611) alátámasztja a szövegalapú szűrés robusztusságát. "
    "A technikai elnöki határozathirdetések leválasztása révén a korpusz kizárólag érdemi politikai "
    "diskurzust reprezentál mindkét kormányváltás első 100 napjában."
)
pdf.multi_cell(114, 3.7, limit_text)
pdf.set_y(max(pdf.get_y(), curr_y + 44))
pdf.ln(2)

pdf.set_font("Arial", "B", 8.5)
pdf.set_text_color(26, 58, 92)
pdf.cell(0, 4.2, "7. Összegzés és reprodukálhatóság", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Arial", "", 8.0)
pdf.set_text_color(20, 20, 20)
summary_text = (
    "A tartalmi szövegelemzés igazolja, hogy az első 100 nap nem pusztán intézményi térfoglalásról szól: "
    "2010-ben a fiskális konszolidáció és a munkaalapú gazdaság megteremtése volt a hajtóerő, míg 2026-ban "
    "a közszolgáltatások (egészségügy, közlekedés) válságkezelése és az európai integráció helyreállítása vezette az agendát. "
    "A teljes elemzés (adatbázis, pipeline scriptek, kódkönyv és MI nyilatkozat) elérhető a kutatási repóban."
)
pdf.multi_cell(0, 3.7, summary_text)
pdf.ln(1)

pdf.set_draw_color(26, 58, 92)
pdf.set_line_width(0.3)
pdf.line(18, pdf.get_y()+1, 192, pdf.get_y()+1)
pdf.ln(2)
pdf.set_font("Arial", "I", 7.2)
pdf.set_text_color(90, 90, 90)
repo_info = (
    "Kutatási repó és reprodukciós csomag: Berczi_Zoltan_Bibo_4blokk_leadando.zip  |  "
    "Adattár: parlament_100nap.db (SQLite, 41 MB), CODEBOOK.pdf, MI_NYILATKOZAT.pdf  |  "
    "Eszközök: Python 3.9, sqlite3, fpdf2, matplotlib."
)
pdf.multi_cell(0, 3.2, repo_info, align="C")

pdf.output(PDF_PATH_LEADANDO)
pdf.output(PDF_PATH_REPO)
print(f"✅ Siker! PDF elkészült:")
print(f"   Leadandó: {PDF_PATH_LEADANDO}")
print(f"   Repó:     {PDF_PATH_REPO}")
print(f"Oldalszám: {pdf.page_no()}")
