import streamlit as st
import database
from datetime import datetime, date

def prikazi_kalendar(username):
    st.subheader("📅 Operativni kalendar i rokovi (ZNR & ZOP)")
    st.markdown("Pregled svih predstojećih rokova i isteka atesta sortiranih po hronološkom redu.")

    svi_rokovi = []

    # A) Opšti rokovi firme (ako imaju definisan datum)
    firme_podaci = database.ucitaj_podatke_firme(username)
    if firme_podaci and "datumi" in firme_podaci:
        for stavka, datum_str in firme_podaci["datumi"].items():
            if datum_str and datum_str != "N/A" and datum_str.startswith("20"):
                svi_rokovi.append({
                    "kategorija": "Opšti rok / Inspekcija",
                    "naziv": stavka,
                    "datum": datum_str,
                    "detalji": "Glavna evidencija obaveza"
                })

    # B) Registar mašina, instalacija i ZOP-a
    masine = database.ucitaj_masine(username)
    for m in masine:
        # m[7] je datum isteka, uzimamo samo ako postoji i validan je
        datum_isteka = m[7] if (len(m) > 7 and m[7] and m[7] != "N/A" and m[7].startswith("20")) else None
        
        if datum_isteka:
            svi_rokovi.append({
                "kategorija": f"Resurs / Oprema ({m[2]})",
                "naziv": m[1],
                "datum": datum_isteka,
                "detalji": f"Serijski br: {m[3] if m[3] else 'N/A'} | Zapisnik/Dozvola: {m[4] if m[4] else 'N/A'}",
                "pdf": m[8] if len(m) > 8 else ""
            })

    # C) Ljekarski pregledi sa unesenim rokom važenja (periodični)
    ljekarski = database.ucitaj_ljekarske(username)
    for lj in ljekarski:
        # lj[5] je datum isteka (ako je unesen za periodične)
        datum_isteka_lj = lj[5] if (len(lj) > 5 and lj[5] and lj[5] != "N/A" and lj[5].startswith("20")) else None
        
        if datum_isteka_lj:
            ustanova_naziv = lj[6] if (len(lj) > 6 and lj[6]) else 'N/A'
            svi_rokovi.append({
                "kategorija": "Ljekarski pregled (Periodični)",
                "naziv": f"{lj[3]} - {lj[1]} ({lj[2]})",
                "datum": datum_isteka_lj,
                "detalji": f"Ustanova: {ustanova_naziv}",
                "pdf": lj[7] if len(lj) > 7 else ""
            })

    if not svi_rokovi:
        st.info("Trenutno nema unesenih stavki sa rokom isteka u sistemu.")
        return

    # Sortiranje po datumu (hronološki)
    svi_rokovi.sort(key=lambda x: x["datum"])

    danas = date.today()

    for rok in svi_rokovi:
        try:
            dt_isteka = datetime.strptime(rok["datum"], "%Y-%m-%d").date()
            dani_razlika = (dt_isteka - danas).days
        except ValueError:
            continue

        if dani_razlika < 0:
            status_ikonica = "🔴"
            status_tekst = f"ISTEKLO prije {abs(dani_razlika)} dana!"
        elif dani_razlika <= 30:
            status_ikonica = "🟡"
            status_tekst = f"Uskoro ističe (za {dani_razlika} dana)"
        else:
            status_ikonica = "🟢"
            status_tekst = f"U redu (još {dani_razlika} dana)"

        with st.container():
            col1, col2, col3 = st.columns([2, 3, 2])
            with col1:
                st.markdown(f"**{status_ikonica} {rok['kategorija']}**")
                st.caption(f"Datum isteka: **{rok['datum']}**")
            with col2:
                st.markdown(f"**{rok['naziv']}**")
                st.text(rok["detalji"])
            with col3:
                st.markdown(f"*{status_tekst}*")
                if "pdf" in rok and rok["pdf"]:
                    st.markdown(f"[📄 Preuzmi zapisnik]({rok['pdf']})")
            st.divider()