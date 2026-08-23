# database.py
import sqlite3
import json
import os

# Definišemo apsolutnu putanju da baza uvijek bude u istom folderu uz skript
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "znr_baza.db")

def inicijalizuj_bazu():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS korisnici (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            podaci_firme TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS masine (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            naziv TEXT,
            kategorija TEXT,
            serijski_broj TEXT,
            broj_dozvole TEXT,
            ovlastena_kuca TEXT,
            datum_pregleda TEXT,
            datum_isteka TEXT,
            pdf_putanja TEXT
        )
    """)

    try:
        cursor.execute("ALTER TABLE masine ADD COLUMN ovlastena_kuca TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS obuke (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            ime_prezime TEXT,
            radno_mjesto TEXT,
            vrsta_obuke TEXT,
            datum_obuke TEXT,
            datum_isteka TEXT,
            napomena TEXT,
            pdf_putanja TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ljekarski (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            ime_prezime TEXT,
            radno_mjesto TEXT,
            tip_pregleda TEXT,
            datum_pregleda TEXT,
            datum_isteka TEXT,
            ustanova TEXT,
            pdf_putanja TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rizicna_mjesta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            naziv_rm TEXT,
            opis_opasnosti TEXT,
            ime_radnika TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opasne_materije (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            naziv_materije TEXT,
            kolicina_skladiste TEXT,
            namjena TEXT,
            posjeduje_sds TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lzo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            ime_prezime TEXT,
            radno_mjesto TEXT,
            naziv_lzo TEXT,
            datum_zaduzenja TEXT,
            napomena TEXT
        )
    """)

    # --- NOVE TABELE ZA ČLAN 61 ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posude_pod_pritiskom (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            naziv_opreme TEXT,
            inventarni_broj TEXT,
            radni_pritisak TEXT,
            datum_pregleda TEXT,
            datum_isteka TEXT,
            ovlastena_kuca TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS povrede_na_radu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            ime_prezime TEXT,
            radno_mjesto TEXT,
            datum_povrede TEXT,
            vrsta_tezina_povrede TEXT,
            uzrok_povrede TEXT,
            prijava_inspekciji TEXT
        )
    """)

    conn.commit()
    conn.close()

def init_db():
    inicijalizuj_bazu()

def ubaci_inicijalne_firme():
    pass

def provjeri_korisnika(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM korisnici WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def provjeri_login(username, password):
    return provjeri_korisnika(username, password)

def dodaj_korisnika(username, password):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        pocetni_podaci = json.dumps({
            "naziv": "",
            "djelatnost": "",
            "radnika": 20,
            "sjediste": "",
            "jib": "",
            "direktor": "",
            "kontakt": "",
            "lokacije": {"Sve lokacije (Sumarni pregled)": []},
            "datumi": {},
            "detalji_periodike": {}
        })
        cursor.execute("INSERT INTO korisnici (username, password, podaci_firme) VALUES (?, ?, ?)", (username, password, pocetni_podaci))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def registruj_novu_firmu(username, password, naziv, djelatnost, radnika, lokacije_mapa, datumi_dict):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        pocetni_podaci = json.dumps({
            "naziv": naziv,
            "djelatnost": djelatnost,
            "radnika": int(radnika) if str(radnika).isdigit() else 20,
            "sjediste": "",
            "jib": "",
            "direktor": "",
            "kontakt": "",
            "lokacije": lokacije_mapa,
            "datumi": datumi_dict,
            "detalji_periodike": {}
        })
        
        cursor.execute("INSERT INTO korisnici (username, password, podaci_firme) VALUES (?, ?, ?)", (username, password, pocetni_podaci))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def ucitaj_podatke_firme(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT podaci_firme FROM korisnici WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        return json.loads(row[0])
    return {}

def snimi_podatke_firme(username, podaci_dict):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    json_data = json.dumps(podaci_dict)
    cursor.execute("UPDATE korisnici SET podaci_firme = ? WHERE username = ?", (json_data, username))
    conn.commit()
    conn.close()

def dodaj_masinu(username, naziv, kategorija, serijski_broj, broj_dozvole, ovlastena_kuca, datum_pregleda, datum_isteka, pdf_putanja=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO masine (username, naziv, kategorija, serijski_broj, broj_dozvole, ovlastena_kuca, datum_pregleda, datum_isteka, pdf_putanja)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, naziv, kategorija, serijski_broj, broj_dozvole, ovlastena_kuca, datum_pregleda, datum_isteka, pdf_putanja))
    conn.commit()
    conn.close()

def ucitaj_masine(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, naziv, kategorija, serijski_broj, broj_dozvole, ovlastena_kuca, datum_pregleda, datum_isteka, pdf_putanja FROM masine WHERE username = ?", (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def dodaj_obuku(username, ime_prezime, radno_mjesto, vrsta_obuke, datum_obuke, datum_isteka, napomena, pdf_putanja=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO obuke (username, ime_prezime, radno_mjesto, vrsta_obuke, datum_obuke, datum_isteka, napomena, pdf_putanja)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, ime_prezime, radno_mjesto, vrsta_obuke, datum_obuke, datum_isteka, napomena, pdf_putanja))
    conn.commit()
    conn.close()

def ucitaj_obuke(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, ime_prezime, radno_mjesto, vrsta_obuke, datum_obuke, datum_isteka, napomena, pdf_putanja FROM obuke WHERE username = ?", (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def dodaj_ljekarski(username, ime_prezime, radno_mjesto, tip_pregleda, datum_pregleda, datum_isteka, ustanova, pdf_putanja=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ljekarski (username, ime_prezime, radno_mjesto, tip_pregleda, datum_pregleda, datum_isteka, ustanova, pdf_putanja)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, ime_prezime, radno_mjesto, tip_pregleda, datum_pregleda, datum_isteka, ustanova, pdf_putanja))
    conn.commit()
    conn.close()

def ucitaj_ljekarske(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, ime_prezime, radno_mjesto, tip_pregleda, datum_pregleda, datum_isteka, ustanova, pdf_putanja FROM ljekarski WHERE username = ?", (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def dodaj_rizicno_mjesto(username, naziv_rm, opis_opasnosti, ime_radnika):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO rizicna_mjesta (username, naziv_rm, opis_opasnosti, ime_radnika) VALUES (?, ?, ?, ?)", (username, naziv_rm, opis_opasnosti, ime_radnika))
    conn.commit()
    conn.close()

def ucitaj_rizicna_mjesta(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, naziv_rm, opis_opasnosti, ime_radnika FROM rizicna_mjesta WHERE username = ?", (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def dodaj_opasnu_materiju(username, naziv, kolicina, namjena, sds):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO opasne_materije (username, naziv_materije, kolicina_skladiste, namjena, posjeduje_sds) VALUES (?, ?, ?, ?, ?)", (username, naziv, kolicina, namjena, sds))
    conn.commit()
    conn.close()

def ucitaj_opasne_materije(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, naziv_materije, kolicina_skladiste, namjena, posjeduje_sds FROM opasne_materije WHERE username = ?", (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def dodaj_lzo(username, ime_prezime, radno_mjesto, naziv_lzo, datum_zaduzenja, napomena):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO lzo (username, ime_prezime, radno_mjesto, naziv_lzo, datum_zaduzenja, napomena) VALUES (?, ?, ?, ?, ?, ?)", (username, ime_prezime, radno_mjesto, naziv_lzo, datum_zaduzenja, napomena))
    conn.commit()
    conn.close()

def ucitaj_lzo(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, ime_prezime, radno_mjesto, naziv_lzo, datum_zaduzenja, napomena FROM lzo WHERE username = ?", (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- NOVE FUNKCIJE ZA POSUDE I POVREDE ---
def dodaj_posudu_pod_pritiskom(username, naziv, inv_br, pritisak, datum_pr, datum_ist, ovl_kuca):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO posude_pod_pritiskom (username, naziv_opreme, inventarni_broj, radni_pritisak, datum_pregleda, datum_isteka, ovlastena_kuca) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                   (username, naziv, inv_br, pritisak, datum_pr, datum_ist, ovl_kuca))
    conn.commit()
    conn.close()

def ucitaj_posude_pod_pritiskom(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, naziv_opreme, inventarni_broj, radni_pritisak, datum_pregleda, datum_isteka, ovlastena_kuca FROM posude_pod_pritiskom WHERE username = ?", (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def dodaj_povredu_na_radu(username, ime, rm, datum, vrsta, uzrok, prijava):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO povrede_na_radu (username, ime_prezime, radno_mjesto, datum_povrede, vrsta_tezina_povrede, uzrok_povrede, prijava_inspekciji) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (username, ime, rm, datum, vrsta, uzrok, prijava))
    conn.commit()
    conn.close()

def ucitaj_povrede_na_radu(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, ime_prezime, radno_mjesto, datum_povrede, vrsta_tezina_povrede, uzrok_povrede, prijava_inspekciji FROM povrede_na_radu WHERE username = ?", (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows