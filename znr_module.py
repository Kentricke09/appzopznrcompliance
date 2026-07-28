# znr_module.py
import streamlit as st
import config
import database
from datetime import date, datetime, timedelta

def prikazi_znr_formu(formData, current_user):
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            padding: 25px;
            border-radius: 12px;
            color: white;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
    </style>
    """, unsafe_allow_html=True)

    naziv_firme = formData.get("naziv", "Kompanija")
    djelatnost = formData.get("djelatnost", "Nije definisano")
    radnika = formData.get("radnika", 0)
    lokacije = formData.get("lokacije", {})
    datumi = formData.get("datumi", {})

    st.markdown(f"""
    <div class="main-header">
        <h2>🛡️ Compliance Command Center</h2>
        <p style="color: #94a3b8; margin-top: 5px;">Kompanija: <b>{naziv_firme}</b> | Djelatnost: {djelatnost} | Ukupno radnika: {radnika}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("📍 **Filtriraj prikaz po lokaciji nadzora:**")
    izabrana_lokacija = st.selectbox("", list(lokacije.keys()), label_visibility="collapsed")
    
    aktivne_stavke = lokacije.get(izabrana_lokacija, [])

    današnji_datum = date.today()
    ukupno_stavki = len(aktivne_stavke)
    istekli_broj = 0
    skoro_istekli_broj = 0
    uredno_broj = 0

    detalji_statusa = []

    for stavka in aktivne_stavke:
        zadnji_pregled_str = datumi.get(stavka, str(današnji_datum))
        try:
            zadnji_pregled = datetime.strptime(zadnji_pregled_str, "%Y-%m-%d").date()
        except ValueError:
            zadnji_pregled = današnji_datum

        mjeseci_roka = config.rokovi_mjeseci.get(stavka, 12)
        
        if mjeseci_roka == 0:
            uredno_broj += 1
            continue

        dana_roka = mjeseci_roka * 30
        istek_rok = zadnji_pregled.toordinal() + dana_roka
        preostalo_dana = istek_rok - današnji_datum.toordinal()

        if preostalo_dana < 0:
            istekli_broj += 1
            detalji_statusa.append((stavka, "isteklo", preostalo_dana))
        elif preostalo_dana <= 30:
            skoro_istekli_broj += 1
            detalji_statusa.append((stavka, "skoro", preostalo_dana))
        else:
            uredno_broj += 1

    procenat = int((uredno_broj / ukupno_stavki * 100)) if ukupno_stavki > 0 else 100

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Status usklađenosti", value=f"{procenat}%", delta="Uredno" if procenat > 75 else "Pažnja", delta_color="normal" if procenat > 75 else "inverse")
    with col2:
        st.metric(label="Aktivni rokovi", value=f"{ukupno_stavki} stavki", delta="Pod kontrolom")
    with col3:
        st.metric(label="Uskoro ističe / Isteklo", value=f"{istekli_broj + skoro_istekli_broj} obaveza", delta="Reagovati", delta_color="inverse")
    with col4:
        st.metric(label="Lokacija nadzora", value=izabrana_lokacija, delta="Aktivno")

    st.markdown("---")
    st.markdown(f"### ⚡ Prioritetne akcije — `{izabrana_lokacija}`")

    if isteklie_stavke := [d for d in detalji_statusa if d[1] == "isteklo"]:
        for stavka, status, preostalo in isteklie_stavke:
            st.error(f"🚨 **Hitna obaveza:** {stavka} (Lokacija: {izabrana_lokacija} | Status: Isteklo prije {abs(preostalo)} dana!)")
            
            with st.form(f"form_update_{stavka}_{izabrana_lokacija}"):
                st.write(f"Unesite novi datum izvršenja za stavku: {stavka}")
                novi_datum = st.date_input("Novi datum prethodnog pregleda:", value=date.today(), key=f"d_up_{stavka}_{izabrana_lokacija}")
                snimi_klik = st.form_submit_button("💾 Snimi i zatvori alarm", use_container_width=True)
                
                if snimi_klik:
                    datumi[stavka] = str(novi_datum)
                    formData["datumi"] = datumi
                    database.snimi_podatke_firme(current_user, formData)
                    st.success(f"✅ Datum uspješno ažuriran za {stavka}!")
                    st.rerun()
    else:
        st.success("✅ Na odabranoj lokaciji nema isteklih zakonskih obaveza! Sve je pod kontrolom.")


def prikazi_administraciju(formData, current_user):
    st.markdown("### ⚙️ Administracija sistema i podešavanja firme")
    st.caption("Kompletna zakonska evidencija prema Članu 61. Zakona o ZNR.")

    lokacije_dict = formData.get("lokacije", {})
    aktivne_stavke = []
    if "Sve lokacije (Sumarni pregled)" in lokacije_dict:
        aktivne_stavke = lokacije_dict["Sve lokacije (Sumarni pregled)"]
    elif lokacije_dict:
        aktivne_stavke = list(lokacije_dict.values())[0]

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📋 Obaveze i rokovi", 
        "🏢 Osnovni podaci", 
        "⚙️ Registar mašina", 
        "📚 Obuke", 
        "🩺 Ljekarski", 
        "⚠️ Rizična mjesta", 
        "🧪 Opasne materije",
        "🪖 Lična zaštitna oprema (LZO)"
    ])

    # --- TAB 1: OBAVEZE I ROKOVI ---
    with tab1:
        st.markdown("#### Podešavanje obaveza, opreme i datumskih rokova")
        datumi_dict = formData.get("datumi", {})
        with st.form("forma_admin_obaveze"):
            nove_odabrane_obaveze = []
            novi_datumi_pregleda = dict(datumi_dict)

            for obaveza in config.klijent_lista:
                je_checked = obaveza in aktivne_stavke
                checked = st.checkbox(obaveza, value=je_checked, key=f"admin_chk_{obaveza}")
                if checked:
                    nove_odabrane_obaveze.append(obaveza)
                    postojeci_datum = datumi_dict.get(obaveza, str(date.today()))
                    try:
                        d_val_default = date.fromisoformat(postojeci_datum)
                    except ValueError:
                        d_val_default = date.today()

                    d_val = st.date_input(f"📅 Datum prethodnog pregleda za: {obaveza}", value=d_val_default, key=f"admin_date_{obaveza}")
                    novi_datumi_pregleda[obaveza] = str(d_val)
                
                st.markdown("<hr style='margin: 5px 0; border: none; border-top: 1px solid #f1f5f9;'>", unsafe_allow_html=True)

            snimi_obaveze_btn = st.form_submit_button("💾 Snimi izmjene obaveza i datuma", use_container_width=True)
            if snimi_obaveze_btn:
                for lok in lokacije_dict:
                    lokacije_dict[lok] =nove_odabrane_obaveze
                
                formData["lokacije"] = lokacije_dict
                formData["datumi"] = novi_datumi_pregleda
                database.snimi_podatke_firme(current_user, formData)
                st.success("✅ Uspješno ažurirane obaveze, oprema i rokovi!")
                st.rerun()

    # --- TAB 2: PROŠIRENI OSNOVNI PODACI ---
    with tab2:
        st.markdown("#### Osnovni podaci o kompaniji")
        with st.form("forma_osnovni_podaci"):
            novi_naziv = st.text_input("Naziv kompanije:", value=formData.get("naziv", ""))
            
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                novo_sjediste = st.text_input("Sjedište / Adresa:", value=formData.get("sjediste", ""))
                novi_jib = st.text_input("ID / JIB broj:", value=formData.get("jib", ""))
            with c_p2:
                novi_direktor = st.text_input("Direktor / Odgovorno lice:", value=formData.get("direktor", ""))
                novi_kontakt = st.text_input("Kontakt telefon / Email:", value=formData.get("kontakt", ""))

            novi_broj_radnika = st.number_input("Ukupan broj zaposlenih radnika:", min_value=1, value=int(formData.get("radnika", 20)))
            
            snimi_osnovno = st.form_submit_button("💾 Snimi osnovne podatke", use_container_width=True)
            if snimi_osnovno:
                formData["naziv"] = novi_naziv.strip()
                formData["sjediste"] = novo_sjediste.strip()
                formData["jib"] = novi_jib.strip()
                formData["direktor"] = novi_direktor.strip()
                formData["kontakt"] = novi_kontakt.strip()
                formData["radnika"] = novi_broj_radnika
                
                database.snimi_podatke_firme(current_user, formData)
                st.success("✅ Osnovni podaci uspješno sačuvani!")
                st.rerun()

    # --- TAB 3: REGISTAR MAŠINA SA AUTOMATSKIM ROKOM ---
    with tab3:
        tacne_masine_stavke = [
            "Radna oprema i strojevi na mehanizirani pogon", 
            "Posude pod pritiskom i kompresori", 
            "Unutrašnji transport (viljuškari, kranovi, paletari)", 
            "Liftovi i teretne platforme", 
            "Kotlovnice i plinske instalacije"
        ]
        ima_masina = any(stavka in aktivne_stavke for stavka in tacne_masine_stavke)
        
        if ima_masina:
            prikazi_registar_masina(current_user)
        else:
            st.info("ℹ️ **Izjava poslodavca:** Kod ovog poslodavca nisu odabrana sredstva rada / mašine na mehanizirani pogon prema važećoj konfiguraciji.")

    with tab4:
        prikazi_evidenciju_obuka(current_user)

    with tab5:
        prikazi_evidenciju_ljekarskih(current_user)

    with tab6:
        if "Radna mjesta sa povećanim rizikom" in aktivne_stavke:
            prikazi_rizicna_mjesta_tab(current_user)
        else:
            st.info("ℹ️ **Izjava poslodavca:** Kod ovog poslodavca nema utvrđenih radnih mjesta sa povećanim rizikom.")

    with tab7:
        if "Opasne hemikalije i materije" in aktivne_stavke:
            prikazi_opasne_materije_tab(current_user)
        else:
            st.info("ℹ️ **Izjava poslodavca:** Kod ovog poslodavca se ne koriste opasne hemikalije.")

    with tab8:
        if "Sredstva i oprema lične zaštite (LZO)" in aktivne_stavke:
            prikazi_lzo_tab(current_user)
        else:
            st.info("ℹ️ **Izjava poslodavca:** Kod ovog poslodavca nisu odabrana sredstva i oprema lične zaštite (LZO).")


def prikazi_registar_masina(username):
    st.markdown("### ⚙️ Registar mašina, opreme i upotrebnih dozvola")
    st.caption("Evidencija radne opreme, strojeva, posuda pod pritiskom i transportnih sredstava (Član 61. Zakona o ZNR).")

    with st.expander("➕ Dodaj novu mašinu / opremu u evidenciju", expanded=True):
        with st.form("forma_nova_masina"):
            naziv_m = st.text_input("Naziv mašine / opreme (npr. Viljuškar Linde, Kompresor):")
            kat_m = st.selectbox("Kategorija opreme:", [
                "Radna oprema i strojevi na mehanizirani pogon",
                "Posude pod pritiskom i kompresori",
                "Unutrašnji transport (viljuškari, kranovi, paletari)",
                "Liftovi i teretne platforme",
                "Kotlovnice i plinske instalacije"
            ])
            
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                ser_br = st.text_input("Evidencijski / Serijski broj:")
                d_pregled = st.date_input("Datum izvršenog pregleda (Izdavanja):", value=date.today())
            with c_col2:
                br_dozv = st.text_input("Broj upotrebne dozvole / izvještaja:")
                
                # AUTOMATSKI IZRAČUN KRAJNJEG ROKA (npr. zakonski periodično važenje za mašine je obično 3 godine / 36 mjeseci)
                # Računamo tačno: datum izdavanja + 3 godine minus 1 dan (kao u tvom primjeru: 1.2.25 -> 31.1.2028)
                try:
                    default_istek = date(d_pregled.year + 3, d_pregled.month, d_pregled.day) - timedelta(days=1)
                except ValueError:
                    # Za slučaj prestupne godine (29. februar)
                    default_istek = date(d_pregled.year + 3, d_pregled.month, 28)

                d_istek = st.date_input("📅 Automatski izračunat datum idućeg pregleda (rok):", value=default_istek)

            submitted_m = st.form_submit_button("Spremi mašinu u evidenciju", use_container_width=True)
            if submitted_m:
                if not naziv_m.strip():
                    st.error("⚠️ Naziv mašine je obavezan!")
                else:
                    database.dodaj_masinu(username, naziv_m, kat_m, ser_br, br_dozv, str(d_pregled), str(d_istek))
                    st.success("✅ Mašina uspješno dodana u registar sa automatskim rokom!")
                    st.rerun()

    st.markdown("---")
    st.markdown("#### Pregled upisanih mašina i opreme")
    masine = database.ucitaj_masine(username)

    if not masine:
        st.info("ℹ️ Trenutno nema unesenih mašina u bazi.")
    else:
        for m in masine:
            m_id, m_naziv, m_kat, m_ser, m_dozv, m_prg, m_ist = m
            with st.container():
                col_info1, col_info2, col_btn = st.columns([3, 2, 1])
                with col_info1:
                    st.markdown(f"**{m_naziv}**")
                    st.caption(f"Kat: {m_kat} | Ser.br: {m_ser if m_ser else 'N/A'}")
                with col_info2:
                    st.text(f"Dozvola: {m_dozv if m_dozv else 'N/A'}\nPregled: {m_prg} | Ističe: {m_ist}")
                with col_btn:
                    if st.button("🗑️ Obriši", key=f"del_masina_{m_id}", use_container_width=True):
                        database.obrisi_masinu(m_id)
                        st.rerun()
                st.markdown("<hr style='margin: 5px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)


def prikazi_evidenciju_obuka(username):
    st.markdown("### 📚 Evidencija obuka iz ZNR i ZOP (Član 61. tačka d)")
    st.caption("Praćenje obuke i provjere znanja radnika iz zaštite na radu i zaštite od požara.")
    # (Tvoj postojeći kod za obuke ostaje isti)

def prikazi_evidenciju_ljekarskih(username):
    st.markdown("### 🩺 Evidencija ljekarskih pregleda radnika")
    # (Tvoj postojeći kod za ljekarske ostaje isti)

def prikazi_rizicna_mjesta_tab(username):
    st.markdown("### ⚠️ Radna mjesta sa povećanim rizikom i raspoređeni radnici")
    # (Tvoj postojeći kod ostaje isti)

def prikazi_opasne_materije_tab(username):
    st.markdown("### 🧪 Opasne materije i hemikalije koje se koriste pri radu")
    # (Tvoj postojeći kod ostaje isti)

def prikazi_lzo_tab(username):
    st.markdown("### 🪖 Evidencija zadužene opreme za ličnu zaštitu (LZO)")
    # (Tvoj postojeći kod ostaje isti)