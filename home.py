import streamlit as st
import sqlite3
import config
import znr_module
import database
import kalendar_module
from datetime import date, datetime, timedelta
import pandas as pd

st.set_page_config(
    page_title="Compliance Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    database.init_db()
    database.ubaci_inicijalne_firme()

    # --- DODAJ OVO OVDJE DA OSIGURAŠ DA TABELA UVIJEK POSTOJI ---
    conn = sqlite3.connect('compliance_manager.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            package_type TEXT,
            status TEXT DEFAULT 'Pending', 
            subscription_start TEXT,
            subscription_end TEXT
        )
    ''')
    conn.commit()
    conn.close()
    # -------------------------------------------------------------

    if 'ulogovan' not in st.session_state:
        st.session_state['ulogovan'] = False
        st.session_state['korisnik_username'] = ""
        st.session_state['prikazi_izvjestaj'] = False
        st.session_state['registracija_mod'] = False

    if not st.session_state['ulogovan']:
        st.markdown("<br><br>", unsafe_allow_html=True)
        col_centar1, col_centar2, col_centar3 = st.columns([1, 1.5, 1])
        
        with col_centar2:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h1>🛡️ Sistem upravljanja ZNR</h1>
                <p style="color: #64748b;">sistem za upravljanje usklađenošću sa ZNR</p>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state['registracija_mod']:
                st.markdown("### 🏢 Registruj novu firmu u sistemu")
                st.caption("Unesite podatke. Nakon registracije, dobićete predračun za uplatu pretplate, a nalog će biti aktiviran nakon evidentiranja uplate.")

                with st.form("forma_registracija"):
                    reg_username = st.text_input("Korisničko ime (za prijavu):")
                    reg_password = st.text_input("Šifra:", type="password")
                    naziv_firme = st.text_input("Naziv kompanije:")
                    djelatnost = st.selectbox("Osnovna djelatnost:", config.industrije_lista)
                    broj_radnika = st.number_input("Ukupan broj zaposlenih radnika:", min_value=1, value=20)
                    unos_lokacija = st.text_input("Lokacije / Pogon(i) (odvojeno zarezom):", value="")
                    
                    st.markdown("---")
                    st.markdown("<b>Izaberite obaveze koje vaša firma posjeduje (datume i detalje unosite kasnije):</b>", unsafe_allow_html=True)
                    
                    odabrane_obaveze = []
                    trenutna_grupa_reg = ""
                    
                    for obaveza, info in config.klijent_konfiguracija.items():
                        grupa = info.get("grupa", "Ostale obaveze")
                        if grupa != trenutna_grupa_reg:
                            st.markdown(f"<br><h6 style='color:#1e293b; margin-bottom: 5px;'>{grupa}</h6>", unsafe_allow_html=True)
                            trenutna_grupa_reg = grupa
                        
                        if st.checkbox(obaveza, value=False, key=f"reg_chk_{obaveza}"):
                            odabrane_obaveze.append(obaveza)

                    st.markdown("<hr style='margin: 15px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
                    submit_reg = st.form_submit_button("🚀 Pošalji zahtjev za pretplatu", use_container_width=True)

                if submit_reg:
                    clean_user = reg_username.strip().lower()
                    clean_pass = reg_password.strip()
                    clean_naziv = naziv_firme.strip()

                    if not clean_user or not clean_pass or not clean_naziv:
                        st.error("⚠️ Molimo popunite korisničko ime, šifru i naziv kompanije!")
                    else:
                        sirove_lokacije = [l.strip() for l in unos_lokacija.split(",") if l.strip()]
                        if not sirove_lokacije:
                            sirove_lokacije = ["Glavna lokacija"]

                        lokacije_mapa = {"Sve lokacije (Sumarni pregled)": odabrane_obaveze}
                        for lok in sirove_lokacije:
                            lokacije_mapa[lok] = odabrane_obaveze

                        uspjeh = database.registruj_novu_firmu(
                            clean_user,
                            clean_pass,
                            clean_naziv,
                            djelatnost,
                            broj_radnika,
                            lokacije_mapa,
                            {} 
                        )

                        if uspjeh:
                            st.success("✅ Zahtjev je uspješno poslat! Vaš nalog je u statusu čekanja na uplatu. Bićete obaviješteni nakon aktivacije.")
                            st.session_state['registracija_mod'] = False
                            st.rerun()
                        else:
                            st.error("⚠️ Korisničko ime već postoji u bazi. Izaberite drugo.")

                st.markdown("<br>", unsafe_allow_html=True)
                col_reg_nazad, _ = st.columns([1, 1])
                with col_reg_nazad:
                    if st.button("⬅️ Nazad na prijavu", use_container_width=True):
                        st.session_state['registracija_mod'] = False
                        st.rerun()

            else:
                with st.form("login_forma"):
                    st.markdown("### 🔐 Prijava u sistem")
                    input_korisnik = st.text_input("Korisničko ime:")
                    input_sifra = st.text_input("Šifra:", type="password")
                    submitted = st.form_submit_button("Prijavi se", use_container_width=True)

                    if submitted:
                        k = input_korisnik.strip().lower()
                        s = input_sifra.strip()
                        
                        # Specijalni uslov za Admin prijavu (Alchemica Admin)
                        if k == "admin" and s == "alchemica2026": # Možeš prilagoditi šifru po želji
                            st.session_state['ulogovan'] = True
                            st.session_state['korisnik_username'] = "admin"
                            st.session_state['prikazi_izvjestaj'] = True
                            st.rerun()
                        else:
                            res = database.provjeri_login(k, s)
                            if res:
                                # Provjeravamo status i pretplatu iz baze podataka
                                conn = sqlite3.connect('compliance_manager.db')
                                cursor = conn.cursor()
                                cursor.execute('SELECT status, subscription_end FROM clients WHERE email = ?', (k,))
                                row = cursor.fetchone()
                                conn.close()
                                
                                if row:
                                    status, sub_end = row
                                    if status == 'Active':
                                        if sub_end and datetime.strptime(sub_end, "%Y-%m-%d") >= datetime.now():
                                            st.session_state['ulogovan'] = True
                                            st.session_state['korisnik_username'] = k
                                            st.session_state['prikazi_izvjestaj'] = True
                                            st.rerun()
                                        else:
                                            st.error("⚠️ Vaša pretplata je istekla. Molimo izvršite obnovu.")
                                    elif status == 'Pending':
                                        st.warning("⚠️ Vaša uplata još uvijek nije evidentirana. Molimo sačekajte verifikaciju od strane administracije.")
                                    else:
                                        st.error("⚠️ Vaš nalog nije aktivan.")
                                else:
                                    # Fallback za stare inicijalne firme iz baze ako nemaju status kolonu
                                    st.session_state['ulogovan'] = True
                                    st.session_state['korisnik_username'] = k
                                    st.session_state['prikazi_izvjestaj'] = True
                                    st.rerun()
                            else:
                                st.error("⚠️ Pogrešno korisničko ime ili šifra!")

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🏢 Registruj novu firmu", use_container_width=True):
                    st.session_state['registracija_mod'] = True
                    st.rerun()

    else:
        current_user = st.session_state['korisnik_username']
        
        # Ako je prijavljen Admin, tretiramo ga posebno
        if current_user == "admin":
            formData = {"naziv": "Alchemica Administrator"}
        else:
            formData = database.ucitaj_podatke_firme(current_user)

        with st.sidebar:
            st.markdown(f"### 👤 Prijavljeni ste kao:")
            st.info(f"**{formData.get('naziv', current_user)}**")
            st.markdown("---")
            
            izbor_modula = st.radio("Izaberite modul:", [
                "Dashboard i Obaveze (ZNR & ZOP)", 
                "Kalendar rokova", 
                "Administracija sistema"
            ])
            st.markdown("---")
            
            # --- ZVANIČNI LINKOVI FBiH ---
            st.markdown("### 🔗 Korisni linkovi (FBiH)")
            st.markdown("[📌 Registar ovlaštenih organizacija](https://fmrsp.gov.ba/registar-ovlastenih-organizacija-za-obavljanje-strucnih-poslova-iz-oblasti-zastite-na-radu)")
            st.markdown("[📜 Zakon o zaštiti na radu](https://fmrsp.gov.ba/zakon-o-zastiti-na-radu)")
            st.markdown("---")
            
            if st.button("🚪 Odjava iz sistema", use_container_width=True):
                st.session_state['ulogovan'] = False
                st.session_state['korisnik_username'] = ""
                st.session_state['prikazi_izvjestaj'] = False
                st.rerun()

        if izbor_modula == "Dashboard i Obaveze (ZNR & ZOP)":
            if current_user == "admin":
                st.warning("Prijavljeni ste kao Administrator. Izaberite 'Administracija sistema' za pregled uplata i klijenata.")
            else:
                znr_module.prikazi_znr_formu(formData, current_user)
        elif izbor_modula == "Kalendar rokova":
            if current_user == "admin":
                st.info("Kalendar rokova je namijenjen za pregled po firmama.")
            else:
                kalendar_module.prikazi_kalendar(current_user)
        else:
            # Sekcija za administraciju i odobravanje uplata (Admin panel)
            if current_user == "admin":
                st.header("🛠️ Alchemica Admin Panel - Upravljanje uplatama")
                st.write("Pregled svih registrovanih firmi i aktivacija pretplata nakon evidentirane uplate.")
                
                conn = sqlite3.connect('compliance_manager.db')
                try:
                    df_clients = pd.read_sql_query("SELECT id, company_name, email, package_type, status, subscription_end FROM clients", conn)
                    st.dataframe(df_clients, use_container_width=True)
                except Exception as e:
                    st.info("Tabela klijenata se kreira ili još nema unosa.")
                    df_clients = pd.DataFrame()
                conn.close()
                
                if not df_clients.empty:
                    st.subheader("Aktivacija naloga klijenta")
                    client_id_to_activate = st.number_input("Unesi ID firme za aktivaciju pretplate", min_value=1, step=1)
                    
                    if st.button("✅ Odobri uplatu i aktiviraj nalog na 1 godinu", use_container_width=True):
                        conn = sqlite3.connect('compliance_manager.db')
                        cursor = conn.cursor()
                        start_date = datetime.now().strftime("%Y-%m-%d")
                        end_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
                        
                        cursor.execute('''
                            UPDATE clients 
                            SET status = 'Active', subscription_start = ?, subscription_end = ? 
                            WHERE id = ?
                        ''', (start_date, end_date, client_id_to_activate))
                        
                        conn.commit()
                        conn.close()
                        st.success(f"Nalog sa ID-jem {client_id_to_activate} je uspješno aktiviran do {end_date}!")
                        st.rerun()
            else:
                znr_module.prikazi_administraciju(formData, current_user)

if __name__ == "__main__":
    main()