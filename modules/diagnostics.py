import streamlit as st
import os
from utils.backup import build_backup_zip_for_user

def show():
    if "user" not in st.session_state:
        st.warning("Effettua il login.");
        return
    email = st.session_state["user"]["email"]
    st.title("💾 Backup dati")
    if st.button("📦 Crea backup ZIP"):
        data, fname = build_backup_zip_for_user(email)
        st.download_button("Scarica backup", data=data, file_name=fname, mime="application/zip")

    st.divider()
    
    st.title("🔍 Diagnostica sistema")

    st.markdown("## ✅ Configurazione Secrets")
    secrets_to_check = [
        "PIVA_EMITTENTE",
        "PEC_USER",
        "PEC_PASS",
        "PEC_PROVIDER"
    ]

    for key in secrets_to_check:
        if key in st.secrets and st.secrets[key]:
            st.success(f"{key}: impostato")
        else:
            st.error(f"{key}: **mancante**")

    st.markdown("---")
    st.markdown("## 📂 Verifica cartelle")

    folders_to_check = [
        "invoices_xml",
        "data/pdf",
        "logs"
    ]

    for folder in folders_to_check:
        if os.path.exists(folder):
            st.success(f"{folder} esiste ✅")
        else:
            st.error(f"{folder} NON esiste ❌")
            if st.button(f"Crea {folder}", key=f"btn_{folder}"):
                os.makedirs(folder, exist_ok=True)
                st.experimental_rerun()

    st.markdown("---")
    st.markdown("## 💾 Stato Database")
    db_path = "data/fatture.db"
    if os.path.exists(db_path):
        size_kb = os.path.getsize(db_path) / 1024
        st.success(f"Database trovato: {db_path} ({size_kb:.1f} KB)")
    else:
        st.error("Database non trovato ❌")

    st.markdown("---")
    st.markdown("## ℹ️ Info ambiente")
    st.write("Versione Streamlit:", st.__version__)
    st.write("Current working dir:", os.getcwd())
