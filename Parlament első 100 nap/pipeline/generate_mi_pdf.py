import os
from fpdf import FPDF

OUT_LEADANDO = "/Users/berczizoltan/Desktop/Berczi_Zoltan_Bibo_4blokk_leadando"
OUT_REPO = "/Users/berczizoltan/Documents/Egyetem/Politikatudomány MA - ELTE/Bibó/Sebők Miklós AI óra/Sebők Miklós AI kalandok/Parlament első 100 nap"
PDF_PATH_LEADANDO = os.path.join(OUT_LEADANDO, "MI_NYILATKOZAT.pdf")
PDF_PATH_REPO = os.path.join(OUT_REPO, "MI_NYILATKOZAT.pdf")

class DeclarationPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_margins(20, 15, 20)
        self.add_font("Arial", "", "/System/Library/Fonts/Supplemental/Arial.ttf")
        self.add_font("Arial", "B", "/System/Library/Fonts/Supplemental/Arial Bold.ttf")
        self.add_font("Arial", "I", "/System/Library/Fonts/Supplemental/Arial Italic.ttf")

    def footer(self):
        self.set_y(-11)
        self.set_font("Arial", "I", 7.5)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, f"Bérczi Zoltán | MI Nyilatkozat | {self.page_no()}. oldal", align="C")

pdf = DeclarationPDF()
pdf.add_page()

pdf.set_font("Arial", "B", 13.5)
pdf.set_text_color(26, 58, 92)
pdf.cell(0, 6.5, "MI NYILATKOZAT", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.set_font("Arial", "B", 10.5)
pdf.cell(0, 5.5, "A Mesterséges Intelligencia (MI) kutatási célú alkalmazásáról", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.ln(1)

pdf.set_font("Arial", "I", 8.2)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 4.2, "Készítő: Bérczi Zoltán  |  Intézmény: ELTE Bibó István Szakkollégium  |  Kurzusvezető: Sebők Miklós", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.cell(0, 4.2, "Kutatási téma: Parlamenti agendabeállítás az első 100 napban (2010 vs. 2026)  |  Dátum: 2026. november 17.", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.set_draw_color(26, 58, 92)
pdf.set_line_width(0.4)
pdf.line(20, pdf.get_y()+1, 190, pdf.get_y()+1)
pdf.ln(3.5)

def section_title(title):
    pdf.set_font("Arial", "B", 9.5)
    pdf.set_text_color(26, 58, 92)
    pdf.cell(0, 4.8, title, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(0.5)

def body_p(text):
    pdf.set_font("Arial", "", 8.2)
    pdf.set_text_color(25, 25, 25)
    pdf.multi_cell(0, 3.8, text)
    pdf.ln(1.2)

def bullet_p(bold_prefix, text):
    pdf.set_font("Arial", "B", 8.2)
    pdf.set_text_color(26, 58, 92)
    pdf.cell(4, 3.8, "• ")
    pdf.cell(pdf.get_string_width(bold_prefix)+1, 3.8, bold_prefix)
    pdf.set_font("Arial", "", 8.2)
    pdf.set_text_color(25, 25, 25)
    pdf.multi_cell(0, 3.8, text)
    pdf.ln(0.8)

section_title("1. A nyilatkozat célja és alapelvei")
body_p(
    "Jelen nyilatkozat az egyetemi és szakkollégiumi követelményeknek megfelelően dokumentálja, "
    "hogy a kutatási feladat során a szerző milyen céllal és mértékben vett igénybe Mesterséges Intelligenciát (MI). "
    "A kutatás során az MI nem a szerzői döntéshozatalt helyettesítette, hanem fejlett kutatási asszisztensként "
    "és programozási segédeszközként működött közre szigorú emberi felügyelet (Human-in-the-loop) mellett."
)

section_title("2. Alkalmazott technológiák és szoftverkörnyezet")
bullet_p("Platform és modellek: ", "Google Antigravity környezet (Gemini LLM modellek).")
bullet_p("Programozási nyelv: ", "Python 3.9 (macOS platform).")
bullet_p("Adattár és könyvtárak: ", "SQLite 3 (parlament_100nap.db, 41 MB), regex (re), matplotlib, fpdf2, openpyxl.")

section_title("3. Az adatokkal végzett munka lépésről lépésre – MI közreműködéssel")
bullet_p("1. Adatgyűjtés (Scraping): ", "Python scraper pipeline a parlament.hu hivatalos naplóihoz. 100%-os ülésszintű lefedettség (gap: 0), 4 826 nyers felszólalás rögzítése a 2010-es és 2026-os első 100 napból.")
bullet_p("2. Adatbázis modellezés: ", "A ParlLawSpeech nemzetközi relációs séma felépítése (speech, politician, bill, parliamentary_group, sitting_day, topic_category táblák és elemzői nézetek).")
bullet_p("3. Adattisztítás és szűrés: ", "A 200 szó alatti bekiabálások elhagyása, valamint az elnöki technikai szavaztatások és határozathirdetések regex-alapú azonosítása és leválasztása (60 db, is_procedural=1). Érdemi minta: 3 813 beszéd.")
bullet_p("4. CAP szakpolitikai kódolás: ", "A Comparative Agendas Project 21 főkategóriájának leképezése szóhatáros regex szabályrendszerrel és irományszám-alapú törvénykapcsolással.")
bullet_p("5. Roll-down torzítás korrekciója: ", "Sebők Miklós visszajelzése alapján a CAP 20 mesterséges torzításának megszüntetése: a valódi intézményi kulcsszavak leválasztása után 620 felszólalás valós szakpolitikai kategóriát kapott, a pártkódok egységesítésre kerültek (party_code), az üres mezők 'N/A'-val feltöltve.")
bullet_p("6. Coder Agreement (Validáció): ", "Vakteszt 20 véletlenszerű felszólaláson, Excel munkalapon (coder_agreement_20_felszólalás.xlsx). A szerző független kézi kódolása alapján számított Cohen-féle kappa: kappa = 0,611 (közepes/jó egyezés; mondatszintű piloton kappa = 0,800).")
bullet_p("7. Teljes szöveges tartalomelemzés (Full-Text Content Scoring): ", "A törvények és beszédek nem csupán a formális címük, hanem a teljes szövegük (full_text, átlagosan 4 321 karakter) szósűrűsége alapján lettek besorolva. Az önkormányzati ügyek a nemzetközi standard szerint a CAP 14-be kerültek (276 db), a gazdasági salátatörvények a CAP 1-be, a napirend előttiek pedig a valós témájukhoz. A CAP 20 aránya 21,0%-ra (802 db) mérséklődött.")
bullet_p("8. Vizualizáció és PDF riport: ", "Tudományos ábrák generálása (matplotlib) és szigorúan 3 oldalas beszámoló összeállítása (fpdf2).")

section_title("4. Emberi felügyelet és szerzői felelősségvállalás")
body_p(
    "A hallgató (Bérczi Zoltán) határozta meg a kutatási fókuszt, a vizsgálati mintát és a tartalmi szűrési paramétereket. "
    "A kurzusvezetői reflexiók értelmezését, a módszertani finomhangolások jóváhagyását, a 20 fős vakteszt kézi kódolását, "
    "valamint a politikatudományi következtetések érvényesítését a szerző önállóan végezte el. A repó teljes egészében reprodukálható."
)
pdf.ln(1.5)

pdf.set_font("Arial", "I", 8.2)
pdf.cell(0, 4.2, "Budapest, 2026. november 17.", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2.5)
pdf.set_font("Arial", "B", 8.8)
pdf.cell(0, 4.2, "Bérczi Zoltán s.k.", new_x="LMARGIN", new_y="NEXT")

pdf.output(PDF_PATH_LEADANDO)
pdf.output(PDF_PATH_REPO)
print("✅ MI Nyilatkozat PDF frissítve.")
