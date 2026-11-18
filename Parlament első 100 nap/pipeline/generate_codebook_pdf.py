#!/usr/bin/env python3
"""
generate_codebook_pdf.py
Generates CODEBOOK.pdf (2 pages) using fpdf2 and system Arial font.
"""
import os
from fpdf import FPDF

REPO_DIR = "/Users/berczizoltan/Documents/Egyetem/Politikatudomány MA - ELTE/Bibó/Sebők Miklós AI óra/Sebők Miklós AI kalandok/Parlament első 100 nap"
OUT_PDF = os.path.join(REPO_DIR, "CODEBOOK.pdf")

class CodebookPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_margins(16, 12, 16)
        self.set_auto_page_break(auto=False)
        self.add_font("Arial", "", "/System/Library/Fonts/Supplemental/Arial.ttf")
        self.add_font("Arial", "B", "/System/Library/Fonts/Supplemental/Arial Bold.ttf")
        self.add_font("Arial", "I", "/System/Library/Fonts/Supplemental/Arial Italic.ttf")

    def footer(self):
        self.set_y(-10)
        self.set_font("Arial", "I", 7.5)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, f"Parlamenti Első 100 Nap Adatbázis | Kódkönyv (Codebook v2.2) | {self.page_no()}. oldal", align="C")

pdf = CodebookPDF()

# ================= PAGE 1 =================
pdf.add_page()
pdf.set_font("Arial", "B", 13)
pdf.set_text_color(26, 58, 92)
pdf.cell(0, 6, "KÓDKÖNYV ÉS ADATMODELL-DOKUMENTÁCIÓ (CODEBOOK)", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.set_font("Arial", "B", 9)
pdf.cell(0, 4.5, "Parlamenti Első 100 Nap Összehasonlító Adatbázis (2010 vs. 2026) — v2.2", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.set_font("Arial", "I", 7.5)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 4, "Standard: ParlLawSpeech & Comparative Agendas Project (CAP) | Készítő: Bérczi Zoltán | 2026. november", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.ln(1)
pdf.set_draw_color(26, 58, 92)
pdf.set_line_width(0.3)
pdf.line(16, pdf.get_y(), 194, pdf.get_y())
pdf.ln(2)

# 1. Áttekintés
pdf.set_font("Arial", "B", 8.8)
pdf.set_text_color(26, 58, 92)
pdf.cell(0, 4.5, "1. Az adatbázis áttekintése és a korpusz paraméterei (parlament_100nap.db)", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Arial", "", 7.8)
pdf.set_text_color(20, 20, 20)
txt_intro = (
    "Az SQLite adatbázis az Országgyűlés hivatalos plenáris naplóiból kinyert, normalizált relációs adatbázis. "
    "Időkerete a 2010-es (2010. május 14. – augusztus 22., Fidesz–KDNP) és a 2026-os (2026. május 9. – augusztus 17., TISZA) "
    "kormányváltás utáni első 100 naptári nap. "
    "Korpusz-méretek: 4 826 nyers felszólalás; 3 873 db >= 200 szavas beszéd; 186 db eljárási, ügyrendi és mandátumigazolási tétel "
    "(is_procedural = 1); 3 687 db érdemi szakpolitikai felszólalás (is_procedural = 0); 127 db törvényjavaslat; 492 politikus entitás."
)
pdf.multi_cell(0, 3.6, txt_intro)
pdf.ln(1.5)

# 2. Táblák
pdf.set_font("Arial", "B", 8.8)
pdf.set_text_color(26, 58, 92)
pdf.cell(0, 4.5, "2. Relációs táblák és kulcsmezők specifikációja", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Arial", "", 7.8)
pdf.set_text_color(20, 20, 20)

tables_desc = [
    ("speech (Felszólalások)", 
     "id (PK, pl. 2010_001_005); period_id (FK: 2010, 2026); sitting_day_id (FK); speaker_name; politician_id (FK); "
     "group_id (FK); speech_type_code (NAPIREND_ELOTTI, HOZZASZOLAS, UGYRENDI, stb.); agenda_item; bill_id (FK); "
     "word_count; full_text; is_procedural (1 = levezető elnöki, ügyrendi vagy mandátumigazolási tétel [n=186], 0 = érdemi vita [n=3 687])."),
    ("speech_classification (CAP besorolás)",
     "speech_id (PK, FK); primary_topic_code (1-23); subtopic_code (alkód, pl. 105, 1202); confidence (0.00-1.00); "
     "cap_classification_method (content_bill_aligned, content_speech_dominant, general_debate, keyword_match); summary."),
    ("bill (Törvényjavaslatok)",
     "id (PK, pl. 2010_T_9); bill_number (T/9); title; short_title; bill_type; submitter_party; governing_status; is_enacted (1/0); "
     "yes_votes, no_votes, abstain_votes; primary_topic_code (1-23); topic_summary; source_url."),
    ("parliamentary_group (Frakciók)",
     "id (PK); name; short_name; party_code (FIDESZ, KDNP, TISZA, MSZP, JOBBIK, LMP, MI_HAZANK, FUGGETLEN); governing_status."),
    ("speech_retrospective_critique (Múltkritika)",
     "speech_id (PK, FK); has_past_critique (1/0); target_era (2002-2010, NER_2010-2026); critique_intensity (alacsony, közepes, magas); excerpts.")
]

for tname, tdesc in tables_desc:
    pdf.set_font("Arial", "B", 7.8)
    pdf.cell(0, 3.8, f"• {tname}:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Arial", "", 7.4)
    pdf.multi_cell(0, 3.4, tdesc)
    pdf.ln(0.8)

# 3. Kódkönyv táblázat (1. rész)
pdf.set_font("Arial", "B", 8.8)
pdf.set_text_color(26, 58, 92)
pdf.cell(0, 4.5, "3. A Comparative Agendas Project (CAP) 21 főkategóriája (1-10)", new_x="LMARGIN", new_y="NEXT")

cap_p1 = [
    ("1", "Makrogazdaság", "Macroeconomics", "Költségvetés, adósság, adótörvények, MNB, infláció, KKV-k"),
    ("2", "Polgári jogok és kisebbségek", "Civil Rights", "Emberi jogok, diszkriminációellenesség, nemzetiségek, romák"),
    ("3", "Egészségügy", "Health", "Kórházak, orvosok, gyógyszerellátás, egészségbiztosítás, várólisták"),
    ("4", "Mezőgazdaság", "Agriculture", "Agrárpolitika, gazdák, termőföld-használat, állattenyésztés, aszály"),
    ("5", "Munkaügy", "Labor", "Foglalkoztatás, minimálbér, szakszervezetek, sztrájkjog, munka törvénykönyve"),
    ("6", "Oktatás", "Education", "Közoktatás, felsőoktatás, egyetemek, pedagógusbérek, szakképzés"),
    ("7", "Környezetvédelem", "Environment", "Klímapolitika, hulladékgazdálkodás, vízvédelem, akkugyárak"),
    ("8", "Energiaügy", "Energy", "Villamos energia, földgáz, Paks, megújulók, rezsicsökkentés, hálózat"),
    ("9", "Bevándorlás és állampolgárság", "Immigration", "Kettős állampolgárság, honosítás, határvédelem, menekültügy"),
    ("10", "Közlekedés", "Transportation", "Vasút (MÁV), autópályák, közúti hálózat, tömegközlekedési tarifák")
]

cw = [12, 48, 38, 80]
pdf.set_font("Arial", "B", 7.2)
pdf.set_fill_color(26, 58, 92)
pdf.set_text_color(255, 255, 255)
for w, h in zip(cw, ["CAP", "Magyar név", "Angol név", "Főbb tartalom és kulcsszavak"]):
    pdf.cell(w, 4.2, h, border=1, align="C", fill=True)
pdf.ln()

pdf.set_font("Arial", "", 7.0)
pdf.set_text_color(20, 20, 20)
for idx, r in enumerate(cap_p1):
    fill = (idx % 2 == 1)
    pdf.set_fill_color(238, 244, 250) if fill else pdf.set_fill_color(255, 255, 255)
    pdf.cell(cw[0], 3.8, r[0], border=1, align="C", fill=fill)
    pdf.cell(cw[1], 3.8, r[1], border=1, align="L", fill=fill)
    pdf.cell(cw[2], 3.8, r[2], border=1, align="L", fill=fill)
    pdf.cell(cw[3], 3.8, r[3], border=1, align="L", fill=fill)
    pdf.ln()

# ================= PAGE 2 =================
pdf.add_page()

pdf.set_font("Arial", "B", 8.8)
pdf.set_text_color(26, 58, 92)
pdf.cell(0, 4.5, "3. A Comparative Agendas Project (CAP) főkategóriái (12-23)", new_x="LMARGIN", new_y="NEXT")

cap_p2 = [
    ("12", "Jog és igazságszolgáltatás", "Law & Crime", "Btk., Ptk., bíróságok, ügyészség, rendőrség, korrupció, elszámoltatás"),
    ("13", "Szociálpolitika és jólét", "Social Welfare", "Családtámogatás, GYES/GYED, nyugdíjak, szociális segélyezés, mélyszegénység"),
    ("14", "Településfejlesztés, önkorm.", "Community Dev.", "Helyi önkormányzatok, településfejlesztés, bérlakás, önkormányzati választás"),
    ("15", "Belkereskedelem, pénzügy", "Domestic Commerce", "Bankrendszer, devizahitelek, bankadó, fogyasztóvédelem, monopóliumok"),
    ("16", "Honvédelem", "Defense", "Magyar Honvédség, NATO kötelezettségek, haderőfejlesztés, védelmi ipar"),
    ("17", "Technológia és média", "Technology & Media", "Médiatörvény, sajtószabadság, digitális infrastruktúra, távközlési felügyelet"),
    ("18", "Külkereskedelem", "Foreign Trade", "Export, import, külpiaci kapcsolatok, nemzetközi vámtarifák"),
    ("19", "Nemzetközi kapcsolatok és EU", "International Affairs", "Európai Unió, RRF források, diplomácia, külpolitikai doktrínák, háborúk"),
    ("20", "Kormányzati működés, alkotmány", "Government Ops", "Alkotmány, Alaptörvény, Alkotmánybíróság, választójog, minisztériumok"),
    ("21", "Állami földek és vízügy", "Public Lands", "Nemzeti Földalap, állami földbérlet, árvízvédelem, folyógazdálkodás"),
    ("23", "Kultúra és vallás", "Culture", "Művészetek, színházak, kulturális örökség, egyházak, NKA támogatások")
]

pdf.set_font("Arial", "B", 7.2)
pdf.set_fill_color(26, 58, 92)
pdf.set_text_color(255, 255, 255)
for w, h in zip(cw, ["CAP", "Magyar név", "Angol név", "Főbb tartalom és kulcsszavak"]):
    pdf.cell(w, 4.2, h, border=1, align="C", fill=True)
pdf.ln()

pdf.set_font("Arial", "", 7.0)
pdf.set_text_color(20, 20, 20)
for idx, r in enumerate(cap_p2):
    fill = (idx % 2 == 1)
    pdf.set_fill_color(238, 244, 250) if fill else pdf.set_fill_color(255, 255, 255)
    pdf.cell(cw[0], 3.8, r[0], border=1, align="C", fill=fill)
    pdf.cell(cw[1], 3.8, r[1], border=1, align="L", fill=fill)
    pdf.cell(cw[2], 3.8, r[2], border=1, align="L", fill=fill)
    pdf.cell(cw[3], 3.8, r[3], border=1, align="L", fill=fill)
    pdf.ln()

pdf.ln(2)

# 4. Módszertani eljárási és kódolási szabályok
pdf.set_font("Arial", "B", 8.8)
pdf.set_text_color(26, 58, 92)
pdf.cell(0, 4.5, "4. Módszertani és procedurális szűrési szabályok", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Arial", "", 7.6)
pdf.set_text_color(20, 20, 20)

rules_text = (
    "1. Elemzési egység és szűrési küszöb: A vizsgálat a ParlLawSpeech nemzetközi standard szerint a legalább 200 szavas "
    "felszólalásokra terjed ki (tisztítva a zárójeles tapsoktól, közbeszólásoktól és teremreakcióktól). "
    "A 200 szó alatti tételek (1 745 db mikro-megszólalás) törlésre kerültek.\n"
    "2. Procedurális kizárás (is_procedural = 1): A 200 szót elérő, de funkciójukban tisztán eljárásrendi felszólalásokat "
    "(levezető elnöki szavaztatás és napirend-lezárás, házszabályi eltérés, bejelentések, eskütétel, mandátumigazolási viták; "
    "összesen n = 186 db) a kutató procedurális kategóriaként különítette el. Az érdemi politikatudományi elemzés bázisa: N = 3 687.\n"
    "3. Tartalmi szövegalapú finomhangolás: A jogszabályok és beszédek besorolása a teljes szöveg tartalomelemzésén alapul. "
    "Az önkormányzati hatáskörök a CAP 14, a gazdasági salátatörvények a CAP 1 és CAP 15 alá kerültek, amivel a CAP 20 aránya "
    "a kezdeti 43,8%-ról 19,9%-ra normalizálódott (732 db az érdemi korpuszban).\n"
    "4. Múltbírálat operacionalizálása: A speech_retrospective_critique tábla azonosítja a korábbi kormányzatok (2002-2010 MSZP-SZDSZ, "
    "illetve 2010-2026 NER) politikai hibáztatását célzó retorikai mintázatokat (n = 806 db)."
)
pdf.multi_cell(0, 3.6, rules_text)
pdf.ln(1.5)

# 5. SQL mintalekérdezés
pdf.set_font("Arial", "B", 8.8)
pdf.set_text_color(26, 58, 92)
pdf.cell(0, 4.5, "5. Ajánlott reprodukciós SQL lekérdezés (Érdemi korpusz, N = 3 687)", new_x="LMARGIN", new_y="NEXT")

sql_code = (
    "SELECT s.id, s.period_id, s.speaker_name, p.party_code, s.speech_type_code,\n"
    "       sc.primary_topic_code, sc.summary, s.word_count\n"
    "FROM speech s\n"
    "JOIN speech_classification sc ON s.id = sc.speech_id\n"
    "LEFT JOIN parliamentary_group p ON s.group_id = p.id\n"
    "WHERE s.word_count >= 200 AND (s.is_procedural = 0 OR s.is_procedural IS NULL);"
)
pdf.set_font("Courier", "", 7.2)
pdf.set_fill_color(240, 243, 246)
pdf.set_draw_color(180, 190, 200)
pdf.multi_cell(0, 3.5, sql_code, border=1, fill=True)

pdf.output(OUT_PDF)
print(f"✅ SIKER: CODEBOOK.pdf legenerálva ide: {OUT_PDF}")
