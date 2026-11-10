# home.py
import streamlit as st
import config
import znr_module
import database
import kalendar_module
from datetime import date
from PIL import Image

st.set_page_config(
    page_title="Compliance Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    database.init_db()
    database.ubaci_inicijalne_firme()

    if 'ulogovan' not in st.session_state:
        st.session_state['ulogovan'] = False
        st.session_state['korisnik_username'] = ""
        st.session_state['prikazi_izvjestaj'] = False
        st.session_state['registracija_mod'] = False

    if not st.session_state['ulogovan']:
        # Dodan CSS za font Inter i specifičan stil zaglavlja
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');
            
            html, body, [class*="st"]  { font-family: 'Inter', sans-serif !important; }
            input, textarea, button, select, div, p, span, label { font-family: 'Inter', sans-serif !important; }
            
            .alchemica-title { 
                font-weight: 400 !important; color: #0f172a; font-size: 1.6rem; 
                text-align: left; letter-spacing: 0.5px; margin: 0 0 2px 0; 
                line-height: 1.2; text-transform: lowercase; 
            }
            .alchemica-subtitle { 
                color: #64748b; font-size: 0.78rem; text-align: left; margin: 0; 
                text-transform: uppercase; font-weight: 400; letter-spacing: 0.3px; 
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)
        col_centar1, col_centar2, col_centar3 = st.columns([1, 1.5, 1])
        
        with col_centar2:
            # Zaglavlje: smanjen razmak i povećan logo (širine [0.6, 3.4], logo 145px)
            head_c1, head_c2 = st.columns([0.6, 3.4], vertical_alignment="center")
            with head_c1:
                try:
                    logo = Image.open("Logo final (2).jpg")
                    st.image(logo, width=145)
                except FileNotFoundError:
                    st.warning("⚠️")
            with head_c2:
                st.markdown('<div class="alchemica-title">compliance command center</div>', unsafe_allow_html=True)
                st.markdown('<div class="alchemica-subtitle">Digitalni sistem za upravljanje zakonskom usklađenošću poslovanja</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            if st.session_state['registracija_mod']:
                st.markdown("### 🏢 Registruj novu firmu u sistemu")
                st.caption("Unesite podatke i definišite pristupne podatke.")

                # Ovdje uvodimo FORMU koja čuva podatke dok se ne pritisne submit dugme
                with st.form("forma_registracija"):
                    reg_username = st.text_input("Korisničko ime (za prijavu):")
                    reg_password = st.text_input("Šifra:", type="password")
                    naziv_firme = st.text_input("Naziv kompanije:")
                    djelatnost = st.selectbox("Osnovna djelatnost:", config.industrije_lista)
                    broj_radnika = st.number_input("Ukupan broj zaposlenih radnika:", min_value=1, value=20)
                    unos_lokacija = st.text_input("Lokacije / Pogon(i) (odvojeno zarezom):", value="Centrala - Sarajevo")
                    
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
                    
                    submit_reg = st.form_submit_button("🚀 Kreiraj nalog i pokreni", use_container_width=True)

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

                        # Upis u bazu
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
                            st.session_state['ulogovan'] = True
                            st.session_state['korisnik_username'] = clean_user
                            st.session_state['prikazi_izvjestaj'] = True
                            st.session_state['registracija_mod'] = False
                            st.success("✅ Uspješno kreiran nalog! Ulazak u sistem...")
                            st.rerun()
                        else:
                            st.error("⚠️ Korisničko ime već postoji u bazi. Izaberite drugo.")

                # Dugme za povratak stoji van forme kako ne bi pokretalo validaciju
                st.markdown("<br>", unsafe_allow_html=True)
                col_reg_nazad, _ = st.columns([1, 1])
                with col_reg_nazad:
                    if st.button("⬅️ Nazad na prijavu", use_container_width=True):
                        st.session_state['registracija_mod'] = False
                        st.rerun()

            else:
                with st.form("login_forma"):
                    # Uklonjen emoji brave
                    st.markdown("### Prijava u sistem")
                    input_korisnik = st.text_input("Korisničko ime:")
                    input_sifra = st.text_input("Šifra:", type="password")
                    submitted = st.form_submit_button("Prijavi se", use_container_width=True)

                    if submitted:
                        k = input_korisnik.strip().lower()
                        s = input_sifra.strip()
                        
                        res = database.provjeri_login(k, s)
                        if res:
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
        formData = database.ucitaj_podatke_firme(current_user)

        # Dodan CSS za maslinasto zelenu boju sidebara (Olive Drab #556b2f)
        st.markdown("""
            <style>
            [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
                background-color: #556b2f !important;
            }
            /* Prilagođavanje boje teksta u sidebaru da bude pregledno na tamnijoj podlozi */
            [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h3 {
                color: #ffffff !important;
            }
            </style>
        """, unsafe_allow_html=True)

        with st.sidebar:
            st.markdown(f"### 👤 Prijavljeni ste kao:")
            st.info(f"**{formData.get('naziv', current_user)}**")
            st.markdown("---")
            # Dodana opcija "Kalendar rokova" u meni
            izbor_modula = st.radio("Izaberite modul:", [
                "Dashboard i Obaveze (ZNR & ZOP)", 
                "Kalendar rokova", 
                "Administracija sistema"
            ])
            st.markdown("---")
            if st.button("🚪 Odjava iz sistema", use_container_width=True):
                st.session_state['ulogovan'] = False
                st.session_state['korisnik_username'] = ""
                st.session_state['prikazi_izvjestaj'] = False
                st.rerun()

        if izbor_modula == "Dashboard i Obaveze (ZNR & ZOP)":
            znr_module.prikazi_znr_formu(formData, current_user)
        elif izbor_modula == "Kalendar rokova":
            kalendar_module.prikazi_kalendar(current_user)
        else:
            znr_module.prikazi_administraciju(formData, current_user)

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
