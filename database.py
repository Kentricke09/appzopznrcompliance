# database.py
import sqlite3
import json
from datetime import date

DB_NAME = "baza.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabela kompanija / korisnika sa proširenim poljima
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kompanije (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            naziv TEXT NOT NULL,
            djelatnost TEXT,
            radnika INTEGER,
            sjediste TEXT,
            jib TEXT,
            direktor TEXT,
            kontakt TEXT
        )
    ''')
    
    # Tabela lokacija i opreme (spremljeno kao JSON tekst za fleksibilnost)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lokacije (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            lokacije_json TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES kompanije (username)
        )
    ''')
    
    # Tabela datuma pregleda opreme
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS datumi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            datumi_json TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES kompanije (username)
        )
    ''')
    
    # Tabela za registar mašina, opreme i upotrebnih dozvola (Član 61)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS masine_oprema (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            naziv_masine TEXT,
            kategorija TEXT,
            serijski_broj TEXT,
            broj_dozvole TEXT,
            datum_pregleda TEXT,
            datum_isteka TEXT
        )
    ''')

    # Tabela za evidenciju obuka (ZNR i ZOP) po radnicima
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS obuke_radnici (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            ime_prezime TEXT,
            radno_mjesto TEXT,
            vrsta_obuke TEXT,
            datum_obuke TEXT,
            datum_isteka TEXT,
            napomena TEXT
        )
    ''')

    # Tabela za evidenciju ljekarskih pregleda po radnicima
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ljekarski_pregledi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            ime_prezime TEXT,
            radno_mjesto TEXT,
            tip_pregleda TEXT,
            datum_pregleda TEXT,
            datum_isteka TEXT,
            zdravstvena_ustanova TEXT
        )
    ''')

    # Tabela za radna mjesta sa povećanim rizikom i radnike na njima
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS radna_mjesta_rizik (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            naziv_radnog_mjesta TEXT,
            opis_opasnosti TEXT,
            ime_radnika TEXT
        )
    ''')

    # Tabela za opasne materije i hemikalije
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS opasne_materije (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            naziv_materije TEXT,
            kolicina_skladiste TEXT,
            namjena TEXT,
            posjeduje_sds TEXT
        )
    ''')

    # Tabela za evidenciju zadužene opreme za ličnu zaštitu (LZO)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lzo_zaduzenja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            ime_radnika TEXT,
            radno_mjesto TEXT,
            naziv_lzo TEXT,
            datum_zaduzenja TEXT,
            napomena TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def ubaci_inicijalne_firme():
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    firme = [
        ("primotronic", "primo2026", "Primotronic d.o.o.", "Elektroenergetika i automatizacija", 35,
         {"Sve lokacije (Sumarni pregled)": ["Periodični ljekarski pregledi", "Vatrogasni aparati (PP aparati)", "Električne i gromobranske instalacije"], "Sarajevo - Uprava": ["Periodični ljekarski pregledi", "Vatrogasni aparati (PP aparati)"], "Tuzla - Pogon": ["Električne i gromobranske instalacije"]},
         {"Periodični ljekarski pregledi": "2025-05-10", "Vatrogasni aparati (PP aparati)": "2026-06-01", "Električne i gromobranske instalacije": "2024-03-15"}
        ),
        ("livi", "livi2026", "Livi d.o.o.", "Tekstilna industrija i konfekcija", 120,
         {"Sve lokacije (Sumarni pregled)": ["Periodični ljekarski pregledi", "Vatrogasni aparati (PP aparati)", "Panik rasvjeta i evakuacioni putevi"], "Zenica - Fabrika": ["Periodični ljekarski pregledi", "Vatrogasni aparati (PP aparati)", "Panik rasvjeta i evakuacioni putevi"]},
         {"Periodični ljekarski pregledi": "2026-02-10", "Vatrogasni aparati (PP aparati)": "2025-11-20", "Panik rasvjeta i evakuacioni putevi": "2024-08-01"}
        ),
        ("granulo", "granulo2026", "Granulo d.o.o.", "Građevinski materijali i separacija", 45,
         {"Sve lokacije (Sumarni pregled)": ["Posude pod pritiskom i kompresori", "Unutrašnji transport (viljuškari, kranovi, paletari)", "Radna mjesta sa povećanim rizikom"], "Kakanj - Separacija": ["Posude pod pritiskom i kompresori", "Unutrašnji transport (viljuškari, kranovi, paletari)"]},
         {"Posude pod pritiskom i kompresori": "2025-04-12", "Unutrašnji transport (viljuškari, kranovi, paletari)": "2025-09-30", "Radna mjesta sa povećanim rizikom": "2025-01-15"}
        )
    ]
    
    for username, pwd, naziv, djelatnost, radnika, lokacije, datumi in firme:
        cursor.execute("SELECT id FROM kompanije WHERE username = ?", (username,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO kompanije (username, password, naziv, djelatnost, radnika) VALUES (?, ?, ?, ?, ?)",
                           (username, pwd, naziv, djelatnost, radnika))
            cursor.execute("INSERT INTO lokacije (username, lokacije_json) VALUES (?, ?)",
                           (username, json.dumps(lokacije)))
            cursor.execute("INSERT INTO datumi (username, datumi_json) VALUES (?, ?)",
                           (username, json.dumps(datumi)))
    
    conn.commit()
    conn.close()

def provjeri_login(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT naziv, djelatnost, radnika FROM kompanije WHERE username = ? AND password = ?", (username, password))
    res = cursor.fetchone()
    conn.close()
    return res

def ucitaj_podatke_firme(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT naziv, djelatnost, radnika, sjediste, jib, direktor, kontakt FROM kompanije WHERE username = ?", (username,))
    comp = cursor.fetchone()
    if not comp:
        conn.close()
        return None
        
    naziv, djelatnost, radnika, sjediste, jib, direktor, kontakt = comp
    
    cursor.execute("SELECT lokacije_json FROM lokacije WHERE username = ?", (username,))
    lok_row = cursor.fetchone()
    lokacije = json.loads(lok_row[0]) if lok_row else {}
    
    cursor.execute("SELECT datumi_json FROM datumi WHERE username = ?", (username,))
    dat_row = cursor.fetchone()
    datumi = json.loads(dat_row[0]) if dat_row else {}
    
    conn.close()
    
    return {
        "naziv": naziv,
        "djelatnost": djelatnost,
        "radnika": radnika,
        "sjediste": sjediste or "",
        "jib": jib or "",
        "direktor": direktor or "",
        "kontakt": kontakt or "",
        "lokacije": lokacije,
        "datumi": datumi
    }

def snimi_podatke_firme(username, formData):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE kompanije 
        SET naziv = ?, djelatnost = ?, radnika = ?, sjediste = ?, jib = ?, direktor = ?, kontakt = ? 
        WHERE username = ?
    """, (
        formData['naziv'], 
        formData.get('djelatnost', ''), 
        formData.get('radnika', 0), 
        formData.get('sjediste', ''), 
        formData.get('jib', ''), 
        formData.get('direktor', ''), 
        formData.get('kontakt', ''), 
        username
    ))
                   
    cursor.execute("UPDATE lokacije SET lokacije_json = ? WHERE username = ?",
                   (json.dumps(formData['lokacije']), username))
                   
    cursor.execute("UPDATE datumi SET datumi_json = ? WHERE username = ?",
                   (json.dumps(formData['datumi']), username))
                   
    conn.commit()
    conn.close()

def registruj_novu_firmu(username, password, naziv, djelatnost, radnika, lokacije, datumi):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO kompanije (username, password, naziv, djelatnost, radnika) VALUES (?, ?, ?, ?, ?)",
                       (username, password, naziv, djelatnost, radnika))
        cursor.execute("INSERT INTO lokacije (username, lokacije_json) VALUES (?, ?)",
                       (username, json.dumps(lokacije)))
        cursor.execute("INSERT INTO datumi (username, datumi_json) VALUES (?, ?)",
                       (username, json.dumps(datumi)))
        conn.commit()
        uspjeh = True
    except sqlite3.IntegrityError:
        uspjeh = False
    conn.close()
    return uspjeh

# --- FUNKCIJE ZA REGISTAR MAŠINA I OPREME ---

def ucitaj_masine(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, naziv_masine, kategorija, serijski_broj, broj_dozvole, datum_pregleda, datum_isteka FROM masine_oprema WHERE username = ?", (username,))
    rezultat = cursor.fetchall()
    conn.close()
    return rezultat

def dodaj_masinu(username, naziv, kategorija, ser_broj, br_dozvole, d_pregleda, d_isteka):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO masine_oprema (username, naziv_masine, kategorija, serijski_broj, broj_dozvole, datum_pregleda, datum_isteka)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (username, naziv, kategorija, ser_broj, br_dozvole, d_pregleda, d_isteka))
    conn.commit()
    conn.close()

def obrisi_masinu(masina_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM masine_oprema WHERE id = ?", (masina_id,))
    conn.commit()
    conn.close()

# --- FUNKCIJE ZA OBUKE RADNIKA ---

def ucitaj_obuke(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, ime_prezime, radno_mjesto, vrsta_obuke, datum_obuke, datum_isteka, napomena FROM obuke_radnici WHERE username = ?", (username,))
    res = cursor.fetchall()
    conn.close()
    return res

def dodaj_obuku(username, ime, radno_mjesto, vrsta, d_obuke, d_isteka, napomena):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO obuke_radnici (username, ime_prezime, radno_mjesto, vrsta_obuke, datum_obuke, datum_isteka, napomena)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (username, ime, radno_mjesto, vrsta, d_obuke, d_isteka, napomena))
    conn.commit()
    conn.close()

def obrisi_obuku(obuka_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM obuke_radnici WHERE id = ?", (obuka_id,))
    conn.commit()
    conn.close()

# --- FUNKCIJE ZA LJEKARSKE PREGLEDE RADNIKA ---

def ucitaj_ljekarske(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, ime_prezime, radno_mjesto, tip_pregleda, datum_pregleda, datum_isteka, zdravstvena_ustanova FROM ljekarski_pregledi WHERE username = ?", (username,))
    res = cursor.fetchall()
    conn.close()
    return res

def dodaj_ljekarski(username, ime, radno_mjesto, tip, d_pregleda, d_isteka, ustanova):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ljekarski_pregledi (username, ime_prezime, radno_mjesto, tip_pregleda, datum_pregleda, datum_isteka, zdravstvena_ustanova)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (username, ime, radno_mjesto, tip, d_pregleda, d_isteka, ustanova))
    conn.commit()
    conn.close()

def obrisi_ljekarski(ljekarski_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ljekarski_pregledi WHERE id = ?", (ljekarski_id,))
    conn.commit()
    conn.close()

# --- FUNKCIJE ZA RADNA MJESTA SA POVEĆANIM RIZIKOM ---

def ucitaj_rizicna_mjesta(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, naziv_radnog_mjesta, opis_opasnosti, ime_radnika FROM radna_mjesta_rizik WHERE username = ?", (username,))
    res = cursor.fetchall()
    conn.close()
    return res

def dodaj_rizicno_mjesto(username, naziv_rm, opis, radnik):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO radna_mjesta_rizik (username, naziv_radnog_mjesta, opis_opasnosti, ime_radnika)
        VALUES (?, ?, ?, ?)
    """, (username, naziv_rm, opis, radnik))
    conn.commit()
    conn.close()

def obrisi_rizicno_mjesto(id_zapis):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM radna_mjesta_rizik WHERE id = ?", (id_zapis,))
    conn.commit()
    conn.close()

# --- FUNKCIJE ZA OPASNE MATERIJE I HEMIKALIJE ---

def ucitaj_opasne_materije(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, naziv_materije, kolicina_skladiste, namjena, posjeduje_sds FROM opasne_materije WHERE username = ?", (username,))
    res = cursor.fetchall()
    conn.close()
    return res

def dodaj_opasnu_materiju(username, naziv, kolicina, namjena, sds):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO opasne_materije (username, naziv_materije, kolicina_skladiste, namjena, posjeduje_sds)
        VALUES (?, ?, ?, ?, ?)
    """, (username, naziv, kolicina, namjena, sds))
    conn.commit()
    conn.close()

def obrisi_opasnu_materiju(id_zapis):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM opasne_materije WHERE id = ?", (id_zapis,))
    conn.commit()
    conn.close()

# --- FUNKCIJE ZA EVIDENCIJU LZO ---

def ucitaj_lzo(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, ime_radnika, radno_mjesto, naziv_lzo, datum_zaduzenja, napomena FROM lzo_zaduzenja WHERE username = ?", (username,))
    res = cursor.fetchall()
    conn.close()
    return res

def dodaj_lzo(username, ime, radno_mjesto, naziv_lzo, datum, napomena):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO lzo_zaduzenja (username, ime_radnika, radno_mjesto, naziv_lzo, datum_zaduzenja, napomena)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, ime, radno_mjesto, naziv_lzo, datum, napomena))
    conn.commit()
    conn.close()

def obrisi_lzo(lzo_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lzo_zaduzenja WHERE id = ?", (lzo_id,))
    conn.commit()
    conn.close()