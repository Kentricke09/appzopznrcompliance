import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date, datetime

# --- PUTANJE DO BAZA PODATAKA ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "znr_baza.db")
COMPLIANCE_DB = os.path.join(BASE_DIR, "compliance_manager.db")

# --- POSTAVKE EMAIL SERVERA (Prilagodite vašim SMTP podacima) ---
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER", "alchemica.znr@gmail.com") # Vaš e-mail za slanje
SMTP_PASS = os.environ.get("SMTP_PASS", "sifra_aplikacije_ovdje")    # Vaša lozinka ili App Password
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "alchemica.znr@gmail.com")

def treba_slati_notifikaciju(preostalo_dana):
    """
    Dinamika obavještavanja:
    - Isteklo ili 0-15 dana do isteka: Svaki dan
    - 16-30 dana do isteka: Svaki drugi dan (parni dani preostalog roka)
    """
    if preostalo_dana <= 15:
        return True
    elif 16 <= preostalo_dana <= 30:
        return preostalo_dana % 2 == 0
    return False

def posalji_email(primaoci, naslov, poruka_html):
    if not primaoci or not SMTP_USER or "sifra_aplikacije_ovdje" in SMTP_PASS:
        print(f"⚠️ Email nije poslat (nedostaju SMTP podaci ili primaoci za {primaoci}).")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = naslov
    msg["From"] = f"Compliance Manager ZNR <{SENDER_EMAIL}>"
    msg["To"] = ", ".join(primaoci)

    msg.attach(MIMEText(poruka_html, "html", "utf-8"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SENDER_EMAIL, primaoci, msg.as_string())
        server.quit()
        print(f"✅ Email uspješno poslat na: {', '.join(primaoci)}")
        return True
    except Exception as e:
        print(f"❌ Greška pri slanju emaila na {primaoci}: {e}")
        return False

def dohvati_emailove_klijenta(username):
    """Pokušava pronaći e-mail adrese klijenta iz baze."""
    primaoci = []
    
    # Prvo provjerava compliance_manager.db (tabela clients)
    if os.path.exists(COMPLIANCE_DB):
        conn = sqlite3.connect(COMPLIANCE_DB)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT email FROM clients WHERE email = ?", (username,))
            row = cursor.fetchone()
            if row and row[0]:
                primaoci.append(row[0].strip())
        except Exception:
            pass
        conn.close()

    # Ako e-mail nije u tabeli clients, koristi sam username ako sadrži '@'
    if not primaoci and "@" in username:
        primaoci.append(username.strip())

    return primaoci

def provjeri_rokove_i_obavijesti():
    if not os.path.exists(DB_NAME):
        print(f"❌ Baza {DB_NAME} ne postoji.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Dohvati sve registre korisnika
    cursor.execute("SELECT DISTINCT username FROM korisnici")
    korisnici = [r[0] for r in cursor.fetchall() if r[0] != "admin"]

    danas = date.today()

    for user in korisnici:
        upozorenja = []

        # 1. PROVJERA PP APARATA (DVOJNI TAJMER)
        cursor.execute("""
            SELECT tip_aparata, inventarni_broj, lokacija, istek_servisa_6m, istek_ispitivanja_5g 
            FROM pp_aparati WHERE username = ?
        """, (user,))
        pp_aparati = cursor.fetchall()
        for pp in pp_aparati:
            tip_p, inv_p, lok_p, istek_6m, istek_5g = pp
            
            # Provjera redovnog servisa (6m)
            if istek_6m:
                try:
                    dt_6m = date.fromisoformat(istek_6m)
                    dani_6m = (dt_6m - danas).days
                    if dani_6m < 0:
                        upozorenja.append(f"🔴 <b>PP aparat {tip_p} (Inv: {inv_p}, Lokacija: {lok_p})</b> — Redovni servis (6m) je <b>ISTEKAO</b> dana {istek_6m}!")
                    elif treba_slati_notifikaciju(dani_6m):
                        upozorenja.append(f"🟡 <b>PP aparat {tip_p} (Inv: {inv_p}, Lokacija: {lok_p})</b> — Redovni servis (6m) ističe za <b>{dani_6m} dana</b> ({istek_6m}).")
                except ValueError:
                    pass

            # Provjera 5-godišnjeg ispitivanja posude
            if istek_5g:
                try:
                    dt_5g = date.fromisoformat(istek_5g)
                    dani_5g = (dt_5g - danas).days
                    if dani_5g < 0:
                        upozorenja.append(f"🔴 <b>PP aparat {tip_p} (Inv: {inv_p}, Lokacija: {lok_p})</b> — Ispitivanje posude (5g) je <b>ISTEKO</b> dana {istek_5g}!")
                    elif treba_slati_notifikaciju(dani_5g):
                        upozorenja.append(f"🟡 <b>PP aparat {tip_p} (Inv: {inv_p}, Lokacija: {lok_p})</b> — Ispitivanje posude (5g) ističe za <b>{dani_5g} dana</b> ({istek_5g}).")
                except ValueError:
                    pass

        # 2. PROVJERA LJEKARSKIH PREGLEDA
        cursor.execute("SELECT ime_prezime, radno_mjesto, datum_isteka FROM ljekarski WHERE username = ?", (user,))
        ljekarski = cursor.fetchall()
        for lj in ljekarski:
            ime, rm, istek = lj
            if istek and istek != "N/A":
                try:
                    dt = date.fromisoformat(istek)
                    dani = (dt - danas).days
                    if dani < 0:
                        upozorenja.append(f"🔴 <b>Ljekarski pregled: {ime} ({rm})</b> — <b>ISTEKAO</b> dana {istek}!")
                    elif treba_slati_notifikaciju(dani):
                        upozorenja.append(f"🟡 <b>Ljekarski pregled: {ime} ({rm})</b> — Ističe za <b>{dani} dana</b> ({istek}).")
                except ValueError:
                    pass

        # 3. PROVJERA OBUKA (ZNR / ZOP)
        cursor.execute("SELECT ime_prezime, vrsta_obuke, datum_isteka FROM obuke WHERE username = ?", (user,))
        obuke = cursor.fetchall()
        for ob in obuke:
            ime, vrsta, istek = ob
            if istek and istek != "N/A":
                try:
                    dt = date.fromisoformat(istek)
                    dani = (dt - danas).days
                    if dani < 0:
                        upozorenja.append(f"🔴 <b>{vrsta}: {ime}</b> — <b>ISTEKLO</b> dana {istek}!")
                    elif treba_slati_notifikaciju(dani):
                        upozorenja.append(f"🟡 <b>{vrsta}: {ime}</b> — Ističe za <b>{dani} dana</b> ({istek}).")
                except ValueError:
                    pass

        # 4. PROVJERA MAŠINA I OPREME
        cursor.execute("SELECT naziv, kategorija, datum_isteka FROM masine WHERE username = ?", (user,))
        masine = cursor.fetchall()
        for m in masine:
            naziv, kat, istek = m
            if istek and istek != "N/A":
                try:
                    dt = date.fromisoformat(istek)
                    dani = (dt - danas).days
                    if dani < 0:
                        upozorenja.append(f"🔴 <b>Atest za opremu/instalacije ({kat}): {naziv}</b> — <b>ISTEKAO</b> dana {istek}!")
                    elif treba_slati_notifikaciju(dani):
                        upozorenja.append(f"🟡 <b>Atest za opremu/instalacije ({kat}): {naziv}</b> — Ističe za <b>{dani} dana</b> ({istek}).")
                except ValueError:
                    pass

        # Ako postoje upozorenja za ovog klijenta, šaljemo email
        if upozorenja:
            primaoci = dohvati_emailove_klijenta(user)
            if primaoci:
                naslov = f"⚠️ Compliance Upozorenje - Rokovi ZNR & ZOP ({danas.strftime('%d.%m.%Y.')})"
                
                poruka_html = f"""
                <html>
                <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
                    <div style="background-color: #1e3a8a; padding: 15px; color: white; text-align: center; border-radius: 5px 5px 0 0;">
                        <h2>🛡️ Compliance Command Center</h2>
                        <p style="margin:0;">Sistem za automatsko praćenje obaveza ZNR i ZOP</p>
                    </div>
                    <div style="padding: 20px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 5px 5px;">
                        <p>Poštovani,</p>
                        <p>Sistem je detektovao obaveze i ateste iz oblasti Zaštite na radu i Zaštite od požara koji zahtijevaju Vašu pažnju:</p>
                        <ul style="background-color: #f8fafc; padding: 15px 15px 15px 30px; border-left: 4px solid #ef4444; list-style-type: none;">
                """
                
                for u in upozorenja:
                    poruka_html += f"<li style='margin-bottom: 10px;'>{u}</li>"

                poruka_html += f"""
                        </ul>
                        <p>Molimo Vas da blagovremeno poduzmete potrebne aktivnosti za obnovu atesta i pregleda.</p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="font-size: 0.85em; color: #64748b;">Ovo je automatska notifikacija generisana od strane Compliance Command Center aplikacije.</p>
                    </div>
                </body>
                </html>
                """

                posalji_email(primaoci, naslov, poruka_html)

    conn.close()

if __name__ == "__main__":
    provjeri_rokove_i_obavijesti()
