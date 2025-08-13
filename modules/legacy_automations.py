
import streamlit as st

from modules.landing import inject_styles
from utils import db
import datetime

def show():
    inject_styles()
    st.title("🤖 Automazioni")

    if "utente" not in st.session_state:
        st.warning("⚠️ Effettua il login per accedere.")
        return

    utente = st.session_state["utente"]

    st.markdown("Attiva alcune automazioni per risparmiare tempo e ridurre dimenticanze.")

    st.subheader("📅 Reminder automatici eventi (24h prima)")
    attiva_reminder = st.toggle("Attiva reminder automatici via email")

    if attiva_reminder:
        eventi = db.lista_eventi_futuri(utente)
        oggi = datetime.date.today()
        domani = oggi + datetime.timedelta(days=1)

        eventi_da_notificare = [
            e for e in eventi
            if datetime.date.fromisoformat(e["data"]) == domani
        ]

        if eventi_da_notificare:
            st.success(f"Trovati {len(eventi_da_notificare)} eventi da notificare per domani.")
            for e in eventi_da_notificare:
                st.info(f"📩 Reminder simulato per evento: '{e['titolo']}' il {e['data']} alle {e['ora']}")
                # Qui in futuro potrai inserire: send_email(cliente_email, oggetto, corpo)
        else:
            st.info("Nessun evento da notificare nelle prossime 24 ore.")

    st.divider()
    st.subheader("🔜 Prossime automazioni (in arrivo)")
    st.markdown("- Invio automatico fatture")
    st.markdown("- Backup programmati su cloud")
    st.markdown("- Promemoria clienti inattivi")
