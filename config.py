# config.py

klijent_konfiguracija = {
    # 1. INTERNI AKTI, PROCJENE I PLANOVI (Temelj sistema)
    "Akt o procjeni rizika": {"periodika": False, "mjeseci": 0, "grupa": "📂 1. INTERNI AKTI, PROCJENE I PLANOVI"},
    "Procjena ugroženosti od požara": {"periodika": False, "mjeseci": 0, "grupa": "📂 1. INTERNI AKTI, PROCJENE I PLANOVI"},
    "Plan zaštite od požara": {"periodika": False, "mjeseci": 0, "grupa": "📂 1. INTERNI AKTI, PROCJENE I PLANOVI"},
    "Pravilnik o zaštiti na radu (interni akt)": {"periodika": False, "mjeseci": 0, "grupa": "📂 1. INTERNI AKTI, PROCJENE I PLANOVI"},
    "Plan evakuacije i spasavanja": {"periodika": False, "mjeseci": 0, "grupa": "📂 1. INTERNI AKTI, PROCJENE I PLANOVI"},
    "Program obuke za zaštitu od požara": {"periodika": False, "mjeseci": 0, "grupa": "📂 1. INTERNI AKTI, PROCJENE I PLANOVI"},

    # 2. ZAŠTITA OD POŽARA (ZOP) I SIGURNOSNI SISTEMI (Aktivni sistemi - 6 mjeseci)
    "Automatski javljači požara": {"periodika": True, "mjeseci": 6, "grupa": "🧯 2. ZAŠTITA OD POŽARA (ZOP) I SIGURNOSNI SISTEMI"},
    "Ručni javljači požara": {"periodika": True, "mjeseci": 6, "grupa": "🧯 2. ZAŠTITA OD POŽARA (ZOP) I SIGURNOSNI SISTEMI"},
    "Automatske prskalice (sprinkleri)": {"periodika": True, "mjeseci": 6, "grupa": "🧯 2. ZAŠTITA OD POŽARA (ZOP) I SIGURNOSNI SISTEMI"},
    "Unutrašnja i vanjska hidrantska mreža": {"periodika": True, "mjeseci": 6, "grupa": "🧯 2. ZAŠTITA OD POŽARA (ZOP) I SIGURNOSNI SISTEMI"},
    "Aparati za početno gašenje požara (PP aparati)": {"periodika": True, "mjeseci": 6, "grupa": "🧯 2. ZAŠTITA OD POŽARA (ZOP) I SIGURNOSNI SISTEMI"},
    "Specijalni sistemi s plinom, pjenom ili aerosolom": {"periodika": True, "mjeseci": 6, "grupa": "🧯 2. ZAŠTITA OD POŽARA (ZOP) I SIGURNOSNI SISTEMI"},
    "Aktivni sistemi zaštite od požara (vatrogasni aparati, gašenje)": {"periodika": True, "mjeseci": 6, "grupa": "🧯 2. ZAŠTITA OD POŽARA (ZOP) I SIGURNOSNI SISTEMI"},
    "Panik rasvjeta i putokazi za evakuaciju": {"periodika": False, "mjeseci": 0, "grupa": "🧯 2. ZAŠTITA OD POŽARA (ZOP) I SIGURNOSNI SISTEMI"},
    "Sistemi za detekciju opasnih plinova (plinodojava)": {"periodika": True, "mjeseci": 6, "grupa": "🧯 2. ZAŠTITA OD POŽARA (ZOP) I SIGURNOSNI SISTEMI"},

    # 3. INSTALACIJE I RADNA SREDINA
    "Električne instalacije": {"periodika": True, "mjeseci": 36, "grupa": "🔌 3. INSTALACIJE I RADNA SREDINA"},
    "Gromobranske instalacije": {"periodika": True, "mjeseci": 24, "grupa": "🔌 3. INSTALACIJE I RADNA SREDINA"},
    "Radno okruženje (mikroklima, buka, osvjetljenje)": {"periodika": True, "mjeseci": 36, "grupa": "🔌 3. INSTALACIJE I RADNA SREDINA"},
    "Sistemi za ventilaciju i odsisavanje": {"periodika": False, "mjeseci": 0, "grupa": "🔌 3. INSTALACIJE I RADNA SREDINA"},
    "Ex-zone (instalacije u protiveksplozivnoj izvedbi)": {"periodika": False, "mjeseci": 0, "grupa": "🔌 3. INSTALACIJE I RADNA SREDINA"},

    # 4. RADNICI (Ljudski resursi, obuke i zdravlje)
    "Periodični ljekarski pregledi (radna mjesta sa povećanim rizikom)": {"periodika": True, "mjeseci": 12, "grupa": "👥 4. RADNICI (Ljudski resursi, obuke i zdravlje)"},
    "Obuka i provjera znanja iz zaštite na radu (ZNR)": {"periodika": False, "mjeseci": 0, "grupa": "👥 4. RADNICI (Ljudski resursi, obuke i zdravlje)"},
    "Obuka i provjera znanja iz zaštite na radu - radna mjesta sa povećanim rizikom (ZNR)": {"periodika": True, "mjeseci": 24, "grupa": "👥 4. RADNICI (Ljudski resursi, obuke i zdravlje)"},
    "Obuka i provjera znanja iz zaštite od požara (ZOP)": {"periodika": True, "mjeseci": 24, "grupa": "👥 4. RADNICI (Ljudski resursi, obuke i zdravlje)"},
    "Sredstva i oprema lične zaštite (LZO)": {"periodika": True, "mjeseci": 36, "grupa": "👥 4. RADNICI (Ljudski resursi, obuke i zdravlje)"},

    # 5. RADNA OPREMA, MAŠINE I TRANSPORT
    "Radna oprema i strojevi na mehanizirani pogon": {"periodika": True, "mjeseci": 36, "grupa": "⚙️ 5. RADNA OPREMA, MAŠINE I TRANSPORT"},
    "Unutrašnji transport (viljuškari, kranovi, paletari)": {"periodika": True, "mjeseci": 36, "grupa": "⚙️ 5. RADNA OPREMA, MAŠINE I TRANSPORT"},
    "Liftovi i teretne platforme": {"periodika": True, "mjeseci": 12, "grupa": "⚙️ 5. RADNA OPREMA, MAŠINE I TRANSPORT"},
    "Rad na visini (skele, ljestve, sigurnosni pojasevi)": {"periodika": True, "mjeseci": 12, "grupa": "⚙️ 5. RADNA OPREMA, MAŠINE I TRANSPORT"},
    "Posude pod pritiskom i kompresori": {"periodika": True, "mjeseci": 36, "grupa": "⚙️ 5. RADNA OPREMA, MAŠINE I TRANSPORT"},
    "Kotlovnice i plinske instalacije": {"periodika": True, "mjeseci": 12, "grupa": "⚙️ 5. RADNA OPREMA, MAŠINE I TRANSPORT"},

    # 6. HEMIKALIJE I OPASNE MATERIJE
    "Opasne hemikalije i materije": {"periodika": False, "mjeseci": 0, "grupa": "🧪 6. HEMIKALIJE I OPASNE MATERIJE"}
}

klijent_lista = list(klijent_konfiguracija.keys())

rokovi_mjeseci = {k: v["mjeseci"] for k, v in klijent_konfiguracija.items()}
periodične_stavke = {k: v["periodika"] for k, v in klijent_konfiguracija.items()}

industrije_lista = [
    "Proizvodnja i prerada",
    "Građevinarstvo",
    "Trgovina na veliko i malo",
    "Hemijska industrija i farmacija",
    "Metalurgija i mašinogradnja",
    "Elektroenergetika, gas i klimatizacija",
    "Vodosnabdijevanje i upravljanje otpadnim vodama",
    "Saobraćaj, skladištenje i poštanske usluge",
    "Ugostiteljstvo, hotelijerstvo i turizam",
    "Informacije i komunikacije (IT i mediji)",
    "Finansijske djelatnosti i osiguranje",
    "Poslovanje nekretninama",
    "Stručne, naučne i tehničke djelatnosti",
    "Administrativne i pomoćne uslužne djelatnosti",
    "Javna uprava i odbrana",
    "Obrazovanje",
    "Zdravstvena i socijalna zaštita",
    "Umjetnost, zabava i rekreacija",
    "Poljoprivreda, šumarstvo i ribarstvo",
    "Rudarstvo i vađenje ruda",
    "Ostale uslužne djelatnosti"
]