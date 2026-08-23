import streamlit as st
import database
import config
from datetime import date, timedelta
import io

# Pokušaj uvoza reportlab-a i fontova za PDF generisanje
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    # Registracija Windows Arial fonta da podržava naše kvačiće (č, ć, š, ž, đ)
    pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
    
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


# --- 1. MODULI ZA KADROVE ---

def prikazi_evidenciju_obuka(username):
    st.markdown("### 📚 Evidencija obuka (Član 61. tačka d)")
    with st.form("forma_obuka"):
        ime_r = st.text_input("Ime i prezime radnika:")
        naziv_obuke = st.selectbox("Vrsta obuke:", ["Obuka iz ZNR", "Obuka iz ZNR - povećani rizik", "Obuka iz ZOP"])
        datum_o = st.date_input("Datum obuke:")
        
        mjeseci_roka = 24
        dani_roka = int(mjeseci_roka * 30.42)
        izracunati_istek = datum_o + timedelta(days=dani_roka)
        st.info(f"📅 Automatski izračunati datum isteka obuke ({mjeseci_roka} mjeseci): **{izracunati_istek}**")

        br_zapisnika = st.text_input("Broj zapisnika:")
        ovlastena_kuca = st.text_input("Ovlaštena organizacija:")
        if st.form_submit_button("Spremi obuku"):
            database.dodaj_obuku(username, ime_r, "N/A", naziv_obuke, str(datum_o), str(izracunati_istek), f"Zapisnik: {br_zapisnika}, Kuća: {ovlastena_kuca}")
            st.success(f"✅ Obuka uspješno spremljena (Istek: {izracunati_istek})!")
            st.rerun()

    st.markdown("#### 📋 Pregled unesenih obuka:")
    obuke_rows = database.ucitaj_obuke(username)
    if obuke_rows:
        data_ob = [["Radnik", "Vrsta obuke", "Datum obuke", "Datum isteka", "Napomena"]] + [[o[1], o[3], o[4], o[5], o[6]] for o in obuke_rows]
        st.table(data_ob)
    else:
        st.info("Nema unesenih obuka.")

def prikazi_evidenciju_ljekarskih(username):
    st.markdown("### 🩺 Ljekarski pregledi (Član 61. tačka g)")
    st.caption("Za prethodne preglede datum isteka nije obavezan, dok se za periodične unosi rok važenja.")
    with st.form("forma_ljekarski"):
        ime_r = st.text_input("Ime i prezime radnika:")
        radno_mjesto = st.text_input("Radno mjesto:")
        tip_pregleda = st.selectbox("Tip pregleda:", ["Prethodni pregled", "Periodični pregled", "Vanredni pregled"])
        datum_pr = st.date_input("Datum pregleda:")
        
        unesi_istek = st.checkbox("Unesi datum isteka (obavezno za periodične preglede)", value=False)
        datum_ist = st.date_input("Datum isteka važenja:") if unesi_istek else None
        
        ustanova = st.text_input("Zdravstvena ustanova / Specijalista:")
        if st.form_submit_button("Spremi ljekarski pregled"):
            database.dodaj_ljekarski(username, ime_r, radno_mjesto, tip_pregleda, str(datum_pr), str(datum_ist) if datum_ist else "N/A", ustanova)
            st.success("✅ Ljekarski pregled uspješno spremljen!")
            st.rerun()

    st.markdown("#### 📋 Pregled ljekarskih pregleda:")
    lj_rows = database.ucitaj_ljekarske(username)
    if lj_rows:
        data_lj = [["Radnik", "Mjesto", "Tip", "Pregled", "Istek", "Ustanova"]] + [[l[1], l[2], l[3], l[4], l[5], l[6]] for l in lj_rows]
        st.table(data_lj)
    else:
        st.info("Nema unesenih ljekarskih pregleda.")

def prikazi_radna_mjesta_sa_povećanim_rizikom_tab(username):
    st.markdown("### ⚠️ Radna mjesta sa povećanim rizikom (Član 61. tač. a i b)")
    with st.form("forma_rizicna"):
        naziv_rm = st.text_input("Naziv radnog mjesta sa povećanim rizikom:")
        opis = st.text_area("Opis opasnosti i štetnosti:")
        radnik = st.text_input("Raspoređeni radnik (ime i prezime):")
        if st.form_submit_button("Spremi rizično mjesto"):
            database.dodaj_rizicno_mjesto(username, naziv_rm, opis, radnik)
            st.success("✅ Rizično mjesto i radnik spremljeni!")
            st.rerun()

    st.markdown("#### 📋 Pregled rizičnih mjesta:")
    rm_rows = database.ucitaj_rizicna_mjesta(username)
    if rm_rows:
        data_rm = [["Radno mjesto", "Opis opasnosti", "Radnik"]] + [[r[1], r[2], r[3]] for r in rm_rows]
        st.table(data_rm)
    else:
        st.info("Nema unesenih rizičnih mjesta.")

def prikazi_lzo_tab(username):
    st.markdown("### 🪖 LZO Zaduženja (Lična zaštitna oprema)")
    standardna_lzo = [
        "Zaštitni šljem", 
        "Zaštitne cipele/čizme sa čeličnom kapicom", 
        "Zaštitne rukavice (kožne/nitrilne)", 
        "Reflektujući prsluk", 
        "Zaštitne naočale", 
        "Antifoni / Čepić za uši", 
        "Zaštitna maska za lice/prašinu",
        "Opasač za rad na visini"
    ]
    with st.form("forma_lzo"):
        ime_r = st.text_input("Ime i prezime radnika:")
        radno_mjesto = st.text_input("Radno mjesto:")
        naziv_lzo = st.selectbox("Izaberi zaštitnu opremu:", standardna_lzo)
        datum_zad = st.date_input("Datum zaduženja:")
        napomena = st.text_input("Napomena / Veličina / Serijski broj:")
        if st.form_submit_button("Zaduži LZO"):
            database.dodaj_lzo(username, ime_r, radno_mjesto, naziv_lzo, str(datum_zad), napomena)
            st.success("✅ LZO zaduženje uspješno evidentirano!")
            st.rerun()

    st.markdown("#### 📋 Pregled LZO zaduženja:")
    lzo_rows = database.ucitaj_lzo(username)
    if lzo_rows:
        data_lzo = [["Radnik", "Radno mjesto", "Oprema", "Datum", "Napomena"]] + [[lz[1], lz[2], lz[3], lz[4], lz[5]] for lz in lzo_rows]
        st.table(data_lzo)
    else:
        st.info("Nema unesenih LZO zaduženja.")

# --- 2. MODULI ZA RESURSE I ZOP ---

def prikazi_registar_masina(username):
    st.markdown("### ⚙️ Resursi, instalacije i oprema (Član 61. tačka e)")
    
    sub_resurs = st.radio("Izaberite oblast ispitivanja / opreme:", [
        "Mašine i oprema", 
        "Električne instalacije", 
        "Gromobranske instalacije", 
        "Posude pod pritiskom",
        "Mikroklima", 
        "Mikroklima i štetnosti (buka, hemikalije...)"
    ], horizontal=True)
    
    st.markdown("---")

    if "Mašine" in sub_resurs:
        with st.form("forma_masina_detaljna"):
            st.markdown("#### ⚙️ Unos mašine / opreme")
            naziv = st.text_input("Naziv mašine / opreme:")
            kategorija = st.selectbox("Kategorija:", ["Radna oprema i strojevi", "Unutrašnji transport", "Liftovi i platforme", "Kotlovnice"])
            ser_inv_br = st.text_input("Serijski ili Inventarni broj:")
            br_dozvole = st.text_input("Broj upotrebne dozvole / atesta:")
            datum_dozvole = st.date_input("Datum upotrebne dozvole:")
            
            mjeseci_roka = config.rokovi_mjeseci.get("Radna oprema i strojevi na mehanizirani pogon", 36)
            dani_roka = int(mjeseci_roka * 30.42)
            izracunati_istek = datum_dozvole + timedelta(days=dani_roka)
            st.info(f"📅 Automatski izračunati datum isteka ({mjeseci_roka} mjeseci): **{izracunati_istek}**")
            
            ovlastena_kuca = st.text_input("Ovlaštena organizacija (ko je izvršio pregled):")
            
            if st.form_submit_button("Spremi mašinu"):
                database.dodaj_masinu(username, naziv, kategorija, ser_inv_br, br_dozvole, ovlastena_kuca, str(datum_dozvole), str(izracunati_istek), "")
                st.success(f"✅ Mašina uspješno spremljena (Istek atesta: {izracunati_istek})!")
                st.rerun()

    elif sub_resurs == "Električne instalacije":
        with st.form("forma_struja"):
            st.markdown("#### ⚡ Pregled i ispitivanje električnih instalacija")
            naziv_objekta = st.text_input("Dio objekta / Pogon / Tabla:", value="Glavni elektro ormar / Pogon")
            br_zapisnika = st.text_input("Broj zapisnika / izvještaja:")
            datum_pr = st.date_input("Datum izvršenog ispitivanja:")
            
            mjeseci_roka = config.rokovi_mjeseci.get("Električne instalacije", 36)
            dani_roka = int(mjeseci_roka * 30.42)
            izracunati_istek = datum_pr + timedelta(days=dani_roka)
            st.info(f"📅 Automatski izračunati datum isteka ({mjeseci_roka} mjeseci): **{izracunati_istek}**")
            
            ovlastena_kuca = st.text_input("Ovlaštena organizacija (izvršilac):")
            
            if st.form_submit_button("Spremi ispitivanje električnih instalacija"):
                database.dodaj_masinu(username, naziv_objekta, "Električne instalacije", "N/A", br_zapisnika, ovlastena_kuca, str(datum_pr), str(izracunati_istek), "")
                st.success(f"✅ Zapisnik za električne instalacije spremljen (Istek: {izracunati_istek})!")
                st.rerun()

    elif sub_resurs == "Gromobranske instalacije":
        with st.form("forma_gromobran"):
            st.markdown("#### ⚡ Pregled i ispitivanje gromobranskih instalacija")
            naziv_objekta = st.text_input("Lokacija / Objekat:", value="Gromobranska instalacija objekta")
            br_zapisnika = st.text_input("Broj zapisnika / izvještaja:")
            datum_pr = st.date_input("Datum izvršenog ispitivanja:")
            
            mjeseci_roka = config.rokovi_mjeseci.get("Gromobranske instalacije", 24)
            dani_roka = int(mjeseci_roka * 30.42)
            izracunati_istek = datum_pr + timedelta(days=dani_roka)
            st.info(f"📅 Automatski izračunati datum isteka ({mjeseci_roka} mjeseci): **{izracunati_istek}**")
            
            ovlastena_kuca = st.text_input("Ovlaštena organizacija (izvršilac):")
            
            if st.form_submit_button("Spremi ispitivanje gromobrana"):
                database.dodaj_masinu(username, naziv_objekta, "Gromobranske instalacije", "N/A", br_zapisnika, ovlastena_kuca, str(datum_pr), str(izracunati_istek), "")
                st.success(f"✅ Zapisnik za gromobrane spremljen (Istek: {izracunati_istek})!")
                st.rerun()

    elif sub_resurs == "Posude pod pritiskom":
        with st.form("forma_posude"):
            st.markdown("#### 🛢️ Evidencija posuda pod pritiskom i ventila sigurnosti")
            naziv_p = st.text_input("Naziv posude / opreme (npr. Kompresor, boca za zrak):")
            inv_br = st.text_input("Inventarni / Serijski broj:")
            pritisak = st.text_input("Radni pritisak (bar):")
            datum_pr = st.date_input("Datum izvršenog pregleda:")
            
            mjeseci_roka = config.rokovi_mjeseci.get("Posude pod pritiskom i kompresori", 36)
            dani_roka = int(mjeseci_roka * 30.42)
            izracunati_istek = datum_pr + timedelta(days=dani_roka)
            st.info(f"📅 Automatski izračunati datum isteka ({mjeseci_roka} mjeseci): **{izracunati_istek}**")
            
            ovl_kuca = st.text_input("Ovlaštena organizacija:")
            
            if st.form_submit_button("Spremi posudu pod pritiskom"):
                database.dodaj_posudu_pod_pritiskom(username, naziv_p, inv_br, pritisak, str(datum_pr), str(izracunati_istek), ovl_kuca)
                st.success(f"✅ Posuda pod pritiskom spremljena (Istek: {izracunati_istek})!")
                st.rerun()

    elif sub_resurs == "Mikroklima" or sub_resurs == "Mikroklima i štetnosti (buka, hemikalije...)":
        with st.form("forma_mikroklima"):
            st.markdown("#### 🌡️ Ispitivanje mikroklime i štetnosti u radnoj sredini")
            naziv_mjesta = st.text_input("Radna zona / Mjesto mjerenja:")
            br_zapisnika = st.text_input("Broj stručnog nalaza / zapisnika:")
            datum_pr = st.date_input("Datum mjerenja:")
            
            mjeseci_roka = config.rokovi_mjeseci.get("Radno okruženje (mikroklima, buka, osvjetljenje)", 36)
            dani_roka = int(mjeseci_roka * 30.42)
            izracunati_istek = datum_pr + timedelta(days=dani_roka)
            st.info(f"📅 Automatski izračunati datum isteka ({mjeseci_roka} mjeseci): **{izracunati_istek}**")
            
            ovlastena_kuca = st.text_input("Ovlaštena laboratorija / kuća:")
            
            if st.form_submit_button("Spremi nalaz mikroklime i štetnosti"):
                database.dodaj_masinu(username, naziv_mjesta, "Radno okruženje (mikroklima, buka, osvjetljenje)", "N/A", br_zapisnika, ovlastena_kuca, str(datum_pr), str(izracunati_istek), "")
                st.success(f"✅ Nalaz mikroklime i štetnosti spremljen (Istek: {izracunati_istek})!")
                st.rerun()

    st.markdown("#### 📋 Pregled unesenih resursa i instalacija:")
    mas_rows = database.ucitaj_masine(username)
    if mas_rows:
        data_mas = [["Naziv", "Kategorija", "Zapisnik", "Pregled", "Istek", "Kuća"]] + [[m[1], m[2], m[4], m[6], m[7], m[5]] for m in mas_rows]
        st.table(data_mas)
    else:
        st.info("Nema unesenih resursa ili instalacija.")

def prikazi_opasne_materije_tab(username):
    st.markdown("### 🧪 Evidencija opasnih materija i hemikalija (Član 61. tačka c)")
    with st.form("forma_materije"):
        naziv = st.text_input("Naziv materije / hemikalije:")
        kolicina = st.text_input("Količina / Skladišni prostor:")
        namjena = st.text_input("Namjena u procesu:")
        sds = st.selectbox("Posjeduje SDS (Sigurnosno-tehnički list):", ["Da", "Ne"])
        if st.form_submit_button("Spremi materiju"):
            database.dodaj_opasnu_materiju(username, naziv, kolicina, namjena, sds)
            st.success("✅ Opasna materija uspješno unesena!")
            st.rerun()

    st.markdown("#### 📋 Pregled opasnih materija:")
    mat_rows = database.ucitaj_opasne_materije(username)
    if mat_rows:
        data_mat = [["Materija", "Količina", "Namjena", "SDS"]] + [[m[1], m[2], m[3], m[4]] for m in mat_rows]
        st.table(data_mat)
    else:
        st.info("Nema unesenih opasnih materija.")

def prikazi_povrede_tab(username):
    st.markdown("### 🚑 Evidencija o povredama na radu (Član 61. tačka f)")
    with st.form("forma_povrede"):
        ime = st.text_input("Ime i prezime radnika:")
        rm = st.text_input("Radno mjesto radnika:")
        datum_p = st.date_input("Datum povrede:")
        vrsta = st.selectbox("Vrsta / Težina povrede:", ["Lakša povreda na radu", "Teža povreda na radu", "Kolektivna povreda", "Smrtna povreda", "Profesionalno oboljenje"])
        uzrok = st.text_area("Opis i uzrok povrede:")
        prijava = st.selectbox("Prijavljeno nadležnoj inspekciji rada:", ["Da", "Ne", "Nije primjenjivo"])
        
        if st.form_submit_button("Spremi evidenciju povrede"):
            database.dodaj_povredu_na_radu(username, ime, rm, str(datum_p), vrsta, uzrok, prijava)
            st.success("✅ Evidencija o povredi na radu uspješno unijeta!")
            st.rerun()

    st.markdown("#### 📋 Pregled povreda na radu:")
    pov_rows = database.ucitaj_povrede_na_radu(username)
    if pov_rows:
        data_pov = [["Radnik", "Radno mjesto", "Datum", "Vrsta", "Prijava"]] + [[p[1], p[2], p[3], p[4], p[6]] for p in pov_rows]
        st.table(data_pov)
    else:
        st.info("Nema evidentiranih povreda na radu.")

def prikazi_zop_tab(username):
    st.markdown("### 🧯 Zaštita od požara (ZOP)")
    with st.form("forma_zop_detaljna"):
        tip = st.selectbox("Element ZOP:", [
            "Aparati za početno gašenje požara (PP aparati)", 
            "Unutrašnja i vanjska hidrantska mreža", 
            "Vatrodojava", 
            "Automatske prskalice (sprinkleri)",
            "Specijalni sistemi s plinom, pjenom ili aerosolom",
            "Sistemi za detekciju opasnih plinova (plinodojava)"
        ])
        
        datum_pregleda = st.date_input("Datum izvršenog pregleda:")
        
        mjeseci_roka = config.rokovi_mjeseci.get(tip, 6)
        dani_roka = int(mjeseci_roka * 30.42)
        izracunati_istek = datum_pregleda + timedelta(days=dani_roka)
        
        st.info(f"📅 Automatski izračunati datum isteka važenja ({mjeseci_roka} mjeseci): **{izracunati_istek}**")
        
        br_zapisnika = st.text_input("Broj zapisnika / izvještaja:")
        ovlastena_kuca = st.text_input("Ovlaštena organizacija / Serviser:")
        
        if st.form_submit_button("Spremi ZOP element"):
            database.dodaj_masinu(username, tip, "ZOP", "N/A", br_zapisnika, ovlastena_kuca, str(datum_pregleda), str(izracunati_istek), "")
            st.success(f"✅ Podaci za {tip} uspješno spremljeni! (Istek: {izracunati_istek})")
            st.rerun()

    st.markdown("#### 📋 Pregled unesenih ZOP elemenata:")
    sve_masine = database.ucitaj_masine(username)
    zop_rows = [m for m in sve_masine if m[2] == "ZOP"]
    if zop_rows:
        data_zop = [["Element ZOP", "Zapisnik", "Pregled", "Istek", "Serviser"]] + [[z[1], z[4], z[6], z[7], z[5]] for z in zop_rows]
        st.table(data_zop)
    else:
        st.info("Nema unesenih ZOP elemenata.")

# --- 3. GLAVNA ADMINISTRACIJA ---
def prikazi_administraciju(formData, current_user):
    st.markdown("### ⚙️ Administracija sistema")
    
    sekcija = st.selectbox("📂 Izaberite sekciju:", [
        "1. Osnovne obaveze (Katalog)",
        "2. Kadrovi i obuke",
        "3. ZOP (Zaštita od požara)",
        "4. Resursi i tehnička dokumentacija",
        "5. Povrede na radu (Član 61. f)"
    ])
    st.markdown("---")

    if "1. Osnovne" in sekcija:
        st.markdown("#### 📋 Katalog zakonskih obaveza (Samo odabir obaveza)")
        st.caption("Označite stavke koje važe za Vašu kompaniju. Datumi i rokovi se automatski povlače iz unosa u administraciji.")
        
        lokacije_dict = formData.get("lokacije", {})
        aktivne = lokacije_dict.get("Sve lokacije (Sumarni pregled)", [])
        
        nove_aktivne = []

        with st.form("forma_katalog_admin"):
            for obaveza, info in config.klijent_konfiguracija.items():
                is_checked = st.checkbox(obaveza, value=(obaveza in aktivne), key=f"cat_{obaveza}")
                if is_checked:
                    nove_aktivne.append(obaveza)
                    if info.get("periodika", False) and info.get("mjeseci", 0) > 0:
                        st.markdown(f"<span style='color: #0284c7; font-size: 0.85em;'>↳ Periodična obaveza (zakonski rok: {info['mjeseci']} mjeseci)</span>", unsafe_allow_html=True)
                st.markdown("---")

            if st.form_submit_button("💾 Spremi izmjene kataloga"):
                formData["lokacije"]["Sve lokacije (Sumarni pregled)"] = nove_aktivne
                database.snimi_podatke_firme(current_user, formData)
                st.success("✅ Katalog uspješno ažuriran!")
                st.rerun()

    elif "2. Kadrovi" in sekcija:
        sub = st.radio("Podmeni:", ["Obuke", "Ljekarski", "Radna mjesta sa povećanim rizikom", "LZO Zaduženja"], horizontal=True)
        if sub == "Obuke": prikazi_evidenciju_obuka(current_user)
        elif sub == "Ljekarski": prikazi_evidenciju_ljekarskih(current_user)
        elif sub == "Radna mjesta sa povećanim rizikom": prikazi_radna_mjesta_sa_povećanim_rizikom_tab(current_user)
        elif sub == "LZO Zaduženja": prikazi_lzo_tab(current_user)
        
    elif "3. ZOP" in sekcija:
        prikazi_zop_tab(current_user)
        
    elif "4. Resursi" in sekcija:
        sub = st.radio("Podmeni:", ["Registar mašina", "Opasne materije"], horizontal=True)
        if sub == "Registar mašina": prikazi_registar_masina(current_user)
        elif sub == "Opasne materije": prikazi_opasne_materije_tab(current_user)

    elif "5. Povrede" in sekcija:
        prikazi_povrede_tab(current_user)


# --- 4. FUNKCIJE ZA GENERISANJE PDF IZVJEŠTAJA ---
def generisi_generalni_pdf(formData, current_user):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Arial-Bold', fontSize=16, textColor=colors.HexColor("#1e3a8a"), spaceAfter=12)
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontName='Arial', fontSize=10)
    
    elements.append(Paragraph(f"<b>GENERALNI IZVJEŠTAJ USKLAĐENOSTI (ZNR & ZOP)</b>", title_style))
    elements.append(Paragraph(f"<b>Kompanija:</b> {formData.get('naziv', current_user)}", normal_style))
    elements.append(Paragraph(f"<b>Djelatnost:</b> {formData.get('djelatnost', 'Nije uneseno')}", normal_style))
    elements.append(Paragraph(f"<b>Broj radnika:</b> {formData.get('radnika', 0)}", normal_style))
    elements.append(Spacer(1, 15))
    
    lokacije_dict = formData.get("lokacije", {})
    aktivne_obaveze = lokacije_dict.get("Sve lokacije (Sumarni pregled)", [])
    
    sve_masine = database.ucitaj_masine(current_user) if current_user else []
    baza_datuma = {}
    for m in sve_masine:
        kat = m[2]
        naziv = m[1]
        istek = m[7] if (len(m) > 7 and m[7]) else "Nije unesen"
        baza_datuma[kat] = istek
        baza_datuma[naziv] = istek

    data = [["Zakonska obaveza / Stavka", "Vrsta", "Zadnji pregled / Status"]]
    
    for obaveza in aktivne_obaveze:
        info = config.klijent_konfiguracija.get(obaveza, {})
        periodika = info.get("periodika", False)
        mjeseci = info.get("mjeseci", 0)
        
        if periodika and mjeseci > 0:
            zadnji = "Nije unesen"
            for kljuc, val in baza_datuma.items():
                if kljuc.lower() in obaveza.lower() or obaveza.lower() in kljuc.lower():
                    zadnji = val
                    break
            vrsta_txt = f"Periodična ({mjeseci} mj.)"
            status_txt = f"Istek atesta: {zadnji}"
        else:
            vrsta_txt = "Trajni / Interni akt"
            status_txt = "Usklađeno"
            
        data.append([obaveza, vrsta_txt, status_txt])
        
    t = Table(data, colWidths=[230, 110, 160])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,-1), 'Arial'),
        ('FONTNAME', (0,0), (-1,0), 'Arial-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def generisi_clan61_pdf(username, formData):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Arial-Bold', fontSize=15, textColor=colors.HexColor("#b91c1c"), spaceAfter=10)
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontName='Arial-Bold', fontSize=11, textColor=colors.HexColor("#1e293b"), spaceBefore=8, spaceAfter=4)
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontName='Arial', fontSize=9)
    
    elements.append(Paragraph(f"<b>IZVJEŠTAJ PO ČLANU 61. ZAKONA O ZAŠTITI NA RADU FBiH</b>", title_style))
    elements.append(Paragraph(f"<b>Poslodavac:</b> {formData.get('naziv', username)} | <b>Datum generisanja:</b> {date.today()}", normal_style))
    elements.append(Spacer(1, 10))
    
    # a) i b) Rizična mjesta i radnici
    elements.append(Paragraph("<b>a) i b) Radnici i radna mjesta sa povećanim rizikom</b>", h2_style))
    rm_rows = database.ucitaj_rizicna_mjesta(username)
    if rm_rows:
        data_rm = [["Radno mjesto", "Opis opasnosti", "Raspoređeni radnik"]] + [[r[1], r[2], r[3]] for r in rm_rows]
        t_rm = Table(data_rm, colWidths=[140, 220, 140])
        t_rm.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('FONTNAME', (0,0), (-1,-1), 'Arial'), ('FONTSIZE', (0,0), (-1,-1), 8)]))
        elements.append(t_rm)
    else:
        elements.append(Paragraph("Nema radnih mjesta sa povećanim rizikom.", normal_style))
    elements.append(Spacer(1, 8))
    
    # c) Opasne materije
    elements.append(Paragraph("<b>c) Opasne materije koje se koriste pri radu</b>", h2_style))
    mat_rows = database.ucitaj_opasne_materije(username)
    if mat_rows:
        data_mat = [["Naziv materije", "Količina / Skladište", "Namjena", "SDS"]] + [[m[1], m[2], m[3], m[4]] for m in mat_rows]
        t_mat = Table(data_mat, colWidths=[130, 130, 140, 100])
        t_mat.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('FONTNAME', (0,0), (-1,-1), 'Arial'), ('FONTSIZE', (0,0), (-1,-1), 8)]))
        elements.append(t_mat)
    else:
        elements.append(Paragraph("Nema opasnih materija.", normal_style))
    elements.append(Spacer(1, 8))

    # d) Obuke
    elements.append(Paragraph("<b>d) Provjera znanja radnika (Obuke iz ZNR i ZOP)</b>", h2_style))
    ob_rows = database.ucitaj_obuke(username)
    if ob_rows:
        data_ob = [["Radnik", "Radno mjesto", "Vrsta obuke", "Datum obuke", "Napomena"]] + [[o[1], o[2], o[3], o[4], o[6]] for o in ob_rows]
        t_ob = Table(data_ob, colWidths=[110, 80, 110, 80, 120])
        t_ob.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('FONTNAME', (0,0), (-1,-1), 'Arial'), ('FONTSIZE', (0,0), (-1,-1), 8)]))
        elements.append(t_ob)
    else:
        elements.append(Paragraph("Nema obuka radnika.", normal_style))
    elements.append(Spacer(1, 8))

    # e) Pregledi i ispitivanja (Mašine, instalacije, posude)
    elements.append(Paragraph("<b>e) Pregledi i ispitivanja radne sredine i sredstava za rad</b>", h2_style))
    mas_rows = database.ucitaj_masine(username)
    if mas_rows:
        data_mas = [["Naziv / Oprema", "Kategorija / Tip", "Broj zapisnika", "Pregled", "Istek", "Kuća"]] + [[m[1], m[2], m[4], m[6], m[7], m[5]] for m in mas_rows]
        t_mas = Table(data_mas, colWidths=[120, 120, 75, 65, 65, 55])
        t_mas.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('FONTNAME', (0,0), (-1,-1), 'Arial'), ('FONTSIZE', (0,0), (-1,-1), 7)]))
        elements.append(t_mas)
    else:
        elements.append(Paragraph("Nema pregleda i ispitivanja mašina i radne sredine.", normal_style))
    elements.append(Spacer(1, 8))

    # f) Povrede na radu
    elements.append(Paragraph("<b>f) Povrede na radu, profesionalna oboljenja i smrtni slučajevi</b>", h2_style))
    pov_rows = database.ucitaj_povrede_na_radu(username)
    if pov_rows:
        data_pov = [["Ime i prezime", "Radno mjesto", "Datum povrede", "Vrsta / Težina", "Uzrok", "Prijava inspekciji"]] + [[p[1], p[2], p[3], p[4], p[5], p[6]] for p in pov_rows]
        t_pov = Table(data_pov, colWidths=[100, 80, 70, 90, 100, 60])
        t_pov.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('FONTNAME', (0,0), (-1,-1), 'Arial'), ('FONTSIZE', (0,0), (-1,-1), 7)]))
        elements.append(t_pov)
    else:
        elements.append(Paragraph("Nema povreda na radu, profesionalnih oboljenja niti smrtnih slučajeva.", normal_style))
    elements.append(Spacer(1, 8))

    # g) Ljekarski pregledi
    elements.append(Paragraph("<b>g) Ljekarski pregledi radnika</b>", h2_style))
    lj_rows = database.ucitaj_ljekarske(username)
    if lj_rows:
        data_lj = [["Ime i prezime", "Radno mjesto", "Tip pregleda", "Datum pregleda", "Istek", "Ustanova"]] + [[l[1], l[2], l[3], l[4], l[5], l[6]] for l in lj_rows]
        t_lj = Table(data_lj, colWidths=[110, 90, 90, 75, 75, 60])
        t_lj.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('FONTNAME', (0,0), (-1,-1), 'Arial'), ('FONTSIZE', (0,0), (-1,-1), 7)]))
        elements.append(t_lj)
    else:
        elements.append(Paragraph("Nema ljekarskih pregleda radnika.", normal_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


# --- 4. DASHBOARD ---
def prikazi_znr_formu(formData, current_user):
    st.markdown("### 📊 Dashboard i Status usklađenosti poslovanja")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Naziv kompanije", formData.get('naziv', current_user))
    with col2:
        st.metric("Djelatnost", formData.get('djelatnost', 'Nije uneseno'))
    with col3:
        st.metric("Broj radnika", formData.get('radnika', 0))
        
    st.markdown("---")
    
    # Sekcija za preuzimanje PDF izvještaja
    st.markdown("#### 📥 Generisanje zvaničnih PDF izvještaja")
    if REPORTLAB_AVAILABLE:
        col_pdf1, col_pdf2 = st.columns(2)
        with col_pdf1:
            pdf_gen_data = generisi_generalni_pdf(formData, current_user)
            st.download_button(
                label="📄 Preuzmi Generalni izvještaj (PDF)",
                data=pdf_gen_data,
                file_name=f"generalni_izvjestaj_{current_user}.pdf",
                mime="application/pdf"
            )
        with col_pdf2:
            pdf_c61_data = generisi_clan61_pdf(current_user, formData)
            st.download_button(
                label="📋 Preuzmi Izvještaj po Članu 61 (PDF)",
                data=pdf_c61_data,
                file_name=f"izvjestaj_clan_61_{current_user}.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("⚠️ Biblioteka `reportlab` nije instalirana. Pokrenite `pip install reportlab` u terminalu da biste omogućili generisanje PDF-a.")

    st.markdown("---")
    st.markdown("#### 🚦 Pregled statusa zakonskih obaveza:")
    
    lokacije_dict = formData.get("lokacije", {})
    aktivne_obaveze = lokacije_dict.get("Sve lokacije (Sumarni pregled)", [])
    
    # Učitaj stvarne unose iz baze (mašine, posude, obuke, lzo)
    sve_masine = database.ucitaj_masine(current_user) if current_user else []
    sve_posude = database.ucitaj_posude_pod_pritiskom(current_user) if current_user else []
    sve_obuke = database.ucitaj_obuke(current_user) if current_user else []
    sve_lzo = database.ucitaj_lzo(current_user) if current_user else []
    
    baza_detalja = {}
    
    # 1. Mapiranje mašina, instalacija i ZOP elemenata
    for m in sve_masine:
        kategorija_stavke = m[2]
        naziv_stavke = m[1]
        datum_istek = m[7] if len(m) > 7 and m[7] else None
        if datum_istek:
            detalj_info = {
                "datum": datum_istek,
                "zapisnik": m[4] if m[4] else "N/A",
                "kuca": m[5] if m[5] else "N/A"
            }
            baza_detalja[kategorija_stavke] = detalj_info
            baza_detalja[naziv_stavke] = detalj_info

    # 2. Mapiranje posuda pod pritiskom
    for p in sve_posude:
        if len(p) > 5 and p[5]:
            baza_detalja["Posude pod pritiskom i kompresori"] = {
                "datum": p[5],
                "zapisnik": p[2] if p[2] else "N/A",
                "kuca": p[6] if len(p) > 6 and p[6] else "N/A"
            }

    # 3. Mapiranje obuka
    for o in sve_obuke:
        vrsta_obuke = o[3]
        datum_isteka_obuke = o[5]
        if datum_isteka_obuke and datum_isteka_obuke != "N/A":
            detalj_obuka = {
                "datum": datum_isteka_obuke,
                "zapisnik": "Evidencija obuke",
                "kuca": o[1]
            }
            baza_detalja[vrsta_obuke] = detalj_obuka
            if "zop" in vrsta_obuke.lower():
                baza_detalja["Obuka i provjera znanja iz zaštite od požara (ZOP)"] = detalj_obuka
            elif "znr" in vrsta_obuke.lower():
                baza_detalja["Obuka i provjera znanja iz zaštite na radu (ZNR)"] = detalj_obuka

    # 4. Mapiranje LZO (Lična zaštitna oprema)
    if sve_lzo:
        zadnji_lzo_datum = sve_lzo[-1][4] if len(sve_lzo[-1]) > 4 else "N/A"
        baza_detalja["Sredstva i oprema lične zaštite (LZO)"] = {
            "datum": zadnji_lzo_datum,
            "zapisnik": "Evidencija zaduženja LZO",
            "kuca": "Interno"
        }

    if aktivne_obaveze:
        for obaveza in aktivne_obaveze:
            info = config.klijent_konfiguracija.get(obaveza, {})
            periodika = info.get("periodika", False)
            mjeseci = info.get("mjeseci", 0)
            
            if periodika and mjeseci > 0:
                nadjena_stavka = None
                for kat, val in baza_detalja.items():
                    if kat.lower() in obaveza.lower() or obaveza.lower() in kat.lower():
                        nadjena_stavka = val
                        break

                if nadjena_stavka:
                    try:
                        zadnji_dat_str = nadjena_stavka["datum"]
                        zapisnik_broj = nadjena_stavka["zapisnik"]
                        kuca_naziv = nadjena_stavka["kuca"]
                        
                        istek_datuma = date.fromisoformat(zadnji_dat_str)
                        preostalo_dana = (istek_datuma - date.today()).days
                        
                        if preostalo_dana < 0:
                            semafor = "🔴 **ISTEKLO!**"
                        elif preostalo_dana <= 30:
                            semafor = "🟡 **U SKORO VRIJEME**"
                        else:
                            semafor = "🟢 **USKLAĐENO**"
                            
                        detalj_boja = f"Važi do: **{zadnji_dat_str}** | Br. zapisnika: *{zapisnik_broj}* | Izvršilac: *{kuca_naziv}*"
                    except Exception:
                        semafor = "🟢 **USKLAĐENO**"
                        detalj_boja = f"Evidentirano (Zaduženje LZO)"
                else:
                    semafor = "🔴 **NIJE USKLAĐENO**"
                    detalj_boja = "Potrebno dopuniti u administraciji"
                
                st.markdown(f"{semafor} &nbsp;&nbsp;|&nbsp;&nbsp; **{obaveza}** — *({detalj_boja})*")
            else:
                st.markdown(f"🟢 **USKLAĐENO** &nbsp;&nbsp;|&nbsp;&nbsp; **{obaveza}** — *[Trajni / Interni akt]*")
    else:
        st.info("Trenutno nemate označenih obaveza. Možete ih izabrati u sekciji Administracija sistema -> 1. Osnovne obaveze (Katalog).")