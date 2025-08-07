
import streamlit as st
from utils import db
import datetime
import os

def show():
    if "utente" not in st.session_state:
        st.error("⚠️ Devi effettuare il login per accedere alla dashboard.")
        return
    utente = st.session_state["utente"]

    st.title(f"📊 Benvenuto, {utente}")
    st.markdown("### Ecco un riepilogo della tua attività recente:")

    # === FATTURE ===
    fatture = db.get_all_invoices(utente)
    totale_fatture = len(fatture)
    totale_importi = sum(f[7] for f in fatture)

    st.metric("📄 Fatture Totali", totale_fatture)
    st.metric("💰 Totale Fatturato", f"€ {totale_importi:.2f}")

    # === EVENTI ===
    eventi = db.lista_eventi_futuri(utente)
    eventi_prossimi = [e for e in eventi if datetime.date.fromisoformat(e["data"]) <= datetime.date.today() + datetime.timedelta(days=7)]

    st.markdown("### 📅 Eventi dei prossimi 7 giorni")
    if eventi_prossimi:
        for e in eventi_prossimi:
            st.markdown(f"- **{e['data']} {e['ora']}** — {e['titolo']}")
    else:
        st.info("Nessun evento in arrivo entro la settimana.")

    # === LOG PEC ===
    st.markdown("### 📬 Ultimi invii PEC")
    log_path = "logs/pec_log.txt"
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            log_lines = f.readlines()
        log_utente = [line for line in log_lines if f"utente: {utente}" in line]
        if log_utente:
            for line in reversed(log_utente[-5:]):
                st.markdown(f"- {line.strip()}")
        else:
            st.info("Nessun invio PEC registrato per questo utente.")
    else:
        st.info("Log PEC non ancora disponibile.")
