
import streamlit as st
from utils import db

def show():
    st.title("📊 Calcolo Tasse - Forfettario")

    if "utente" not in st.session_state:
        st.warning("⚠️ Effettua il login per accedere.")
        return

    utente = st.session_state["utente"]

    st.markdown("🔍 Questa simulazione riguarda solo il **regime forfettario**.")
    st.markdown("💡 Usa i dati delle fatture registrate per calcolare l’imposta sostitutiva.")

    coefficiente_redditivita = st.selectbox("📈 Coefficiente di redditività", [78, 67, 40, 86], index=0)
    aliquota = st.radio("💸 Aliquota imposta sostitutiva", ["15%", "5% (startup)"])
    percentuale = 0.05 if "5" in aliquota else 0.15

    fatture = db.get_all_invoices(utente)
    fatturato = sum(f[7] for f in fatture) if fatture else 0.0

    reddito_imponibile = fatturato * (coefficiente_redditivita / 100)
    imposta = reddito_imponibile * percentuale

    st.divider()

    st.markdown(f"**📌 Totale fatturato:** € {fatturato:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.markdown(f"**📌 Reddito imponibile ({coefficiente_redditivita}%):** € {reddito_imponibile:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.markdown(f"**📌 Imposta sostitutiva ({int(percentuale*100)}%):** € {imposta:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.info("🔔 Questa è una simulazione. La dichiarazione dei redditi deve essere fatta con un commercialista.")
