# config.py

industrije_lista = [
    "Proizvodnja, pogoni i mašinogradnja",
    "Hemijska industrija i laboratorije",
    "Građevinarstvo i izvođenje radova",
    "Trgovina, maloprodaja i skladišta",
    "Ugostiteljstvo i turizam (Restorani, hoteli, kafići)",
    "IT, softverske i komunikacijske usluge",
    "Knjigovodstvo, finansije i uredsko poslovanje",
    "Zdravstvenštvo, obrazovanje i javne ustanove",
    "Zanatstvo i uslužni obrti",
    "Poljoprivreda, komunalne djelatnosti i otpad"
]

klijent_lista = [
    # --- ZNR (Zaštita na radu) i Opšta oprema ---
    "Periodični ljekarski pregledi",
    "Rad na visini (skele, ljestve, sigurnosni pojasevi)",
    "Sredstva i oprema lične zaštite (LZO)",
    "Posude pod pritiskom i kompresori",
    "Unutrašnji transport (viljuškari, kranovi, paletari)",
    "Liftovi i teretne platforme",
    "Radna oprema i strojevi na mehanizirani pogon",
    "Opasne hemikalije i materije",
    "Kotlovnice i plinske instalacije",
    "Električne i gromobranske instalacije",
    "Sistemi za ventilaciju i odsisavanje",
    "Ex-zone (instalacije u protiveksplozivnoj izvedbi)",
    "Radno okruženje (mikroklima, buka, osvjetljenje)",
    
    # --- Obuke i provjera znanja (Član 61. tačka d) ---
    "Obuka i provjera znanja iz zaštite na radu (ZNR)",
    "Obuka i provjera znanja iz zaštite od požara (ZOP)",
    
    # --- ZOP (Zaštita od požara) ---
    "Vatrogasni aparati (PP aparati)",
    "Unutrašnja i vanjska hidrantska mreža",
    "Aktivni sistemi zaštite od požara (vatrojava, gašenje)",
    "Panik rasvjeta i evakuacioni putevi",
    "Sistemi za detekciju opasnih plinova (plinodojava)",
    
    # --- Zakonski akti i dokumentacija ---
    "Akt o procjeni rizika",
    "Plan evakuacije i spasavanja",
    "Pravilnik o zaštiti na radu (interni akt)"
]

rokovi_mjeseci = {
    # --- ZNR rokovi ---
    "Periodični ljekarski pregledi": 12,
    "Rad na visini (skele, ljestve, sigurnosni pojasevi)": 6,
    "Sredstva i oprema lične zaštite (LZO)": 12,
    "Posude pod pritiskom i kompresori": 24,
    "Unutrašnji transport (viljuškari, kranovi, paletari)": 12,
    "Liftovi i teretne platforme": 12,
    "Radna oprema i strojevi na mehanizirani pogon": 12,
    "Opasne hemikalije i materije": 12,
    "Kotlovnice i plinske instalacije": 12,
    "Električne i gromobranske instalacije": 48,
    "Sistemi za ventilaciju i odsisavanje": 12,
    "Ex-zone (instalacije u protiveksplozivnoj izvedbi)": 12,
    "Radno okruženje (mikroklima, buka, osvjetljenje)": 36,
    
    # --- Obuke rokovi ---
    "Obuka i provjera znanja iz zaštite na radu (ZNR)": 36,
    "Obuka i provjera znanja iz zaštite od požara (ZOP)": 24,
    
    # --- ZOP rokovi ---
    "Vatrogasni aparati (PP aparati)": 6,
    "Unutrašnja i vanjska hidrantska mreža": 12,
    "Aktivni sistemi zaštite od požara (vatrojava, gašenje)": 12,
    "Panik rasvjeta i evakuacioni putevi": 12,
    "Sistemi za detekciju opasnih plinova (plinodojava)": 6,
    
    # --- Dokumenti (nemaju vremenski rok/periodičnost) ---
    "Akt o procjeni rizika": 0,
    "Plan evakuacije i spasavanja": 0,
    "Pravilnik o zaštiti na radu (interni akt)": 0
}