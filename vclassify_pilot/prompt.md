# Prompt Specification: CAP Major Topic Classification (v1.0)
Date: 2026-11-11
Task: Classify Hungarian parliamentary speech texts into Comparative Agendas Project (CAP) major topics.

## Allowed Codes
- CAP_1: Makrogazdaság
- CAP_2: Polgári jogok és kisebbségek
- CAP_3: Egészségügy
- CAP_4: Mezőgazdaság
- CAP_5: Munkaügy
- CAP_6: Oktatás
- CAP_7: Környezetvédelem
- CAP_8: Energiaügy
- CAP_9: Bevándorlás és állampolgárság
- CAP_10: Közlekedés
- CAP_12: Jog, igazságszolgáltatás és közbiztonság
- CAP_13: Szociálpolitika és jólét
- CAP_14: Lakásügy és településfejlesztés
- CAP_15: Belkereskedelem és pénzügyi szektor
- CAP_16: Honvédelem és katonapolitika
- CAP_17: Technológia, média és távközlés
- CAP_19: Nemzetközi kapcsolatok és külügyek
- CAP_20: Kormányzati működés, alkotmányosság és választások
- CAP_21: Állami földek és vízgazdálkodás
- CAP_23: Kultúra
- NONE: Nem besorolható
- UNREADABLE: Olvashatatlan / technikai hiba

## Output Format
Each file must receive:
1. `file`: Exact filename (e.g. 2010_001_005.txt)
2. `code`: Exactly one code from the list above
3. `reason`: Concise explanation of at most 20 words
4. `sentence`: Exactly one sentence copied VERBATIM from the file demonstrating the topic
5. `model`: Model name and version
6. `prompt_version`: v1.0
