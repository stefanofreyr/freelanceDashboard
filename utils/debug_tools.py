import streamlit as st
import os
import platform
import datetime
import logging

def debug_panel():
    """Mostra pannello debug se attivo in secrets.toml"""
    debug_enabled = st.secrets.get("DEBUG_MODE", False)
    if not debug_enabled:
        return  # niente debug se non attivo

    st.sidebar.markdown("### 🛠 Modalità Debug Attiva")

    # Info sistema
    st.sidebar.write("**Sistema:**", platform.platform())
    st.sidebar.write("**Python:**", platform.python_version())
    st.sidebar.write("**Ora server:**", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Stato sessione
    with st.sidebar.expander("📦 Session State", expanded=False):
        st.json({k: str(v) for k, v in st.session_state.items()})

    # Log file app.log
    log_path = os.path.join("logs", "app.log")
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        last_lines = "".join(lines[-20:])  # ultime 20 righe
        with st.sidebar.expander("📜 Ultimi log", expanded=False):
            st.text(last_lines)
    else:
        st.sidebar.info("Nessun log disponibile.")
