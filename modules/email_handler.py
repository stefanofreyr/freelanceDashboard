
import streamlit as st
import os

def show():
    st.title("📬 Gestione Email")

    if "utente" not in st.session_state:
        st.warning("⚠️ Effettua il login per accedere.")
        return

    st.markdown("Visualizza la cronologia delle email inviate dalla piattaforma.")

    log_path = "logs/email_log.txt"
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as file:
            contenuto = file.read()
        st.text_area("📜 Log Email Inviate", contenuto, height=300)

        if st.button("🗑️ Cancella log email"):
            os.remove(log_path)
            st.success("Log email cancellato.")
    else:
        st.info("Nessun log email trovato.")

    st.divider()
    st.subheader("📧 Compositore rapido (in arrivo)")
    st.markdown("- Invio manuale di email a clienti")
    st.markdown("- Template personalizzabili per fatture, reminder e follow-up")
