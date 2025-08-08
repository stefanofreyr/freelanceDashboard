
import streamlit as st
import os
from utils import db

def show():
    if "utente" not in st.session_state:
        st.error("⚠️ Effettua il login per accedere alla sezione documenti.")
        return

    utente = st.session_state["utente"]
    st.title("📂 Documenti per Cliente")

    # === SELEZIONA CLIENTE ===
    clienti = db.lista_clienti(utente)
    nomi_clienti = [c["nome"] for c in clienti]

    if not nomi_clienti:
        st.warning("⚠️ Nessun cliente disponibile. Aggiungi prima almeno un cliente.")
        return

    cliente_selezionato = st.selectbox("👤 Seleziona un cliente", nomi_clienti)

    # === UPLOAD FILE ===
    st.subheader("📤 Carica un documento")
    uploaded_file = st.file_uploader("Seleziona file", type=None)
    tag = st.text_input("🏷️ Tag opzionale (es: Contratto, Fattura, Ricevuta)")

    if uploaded_file:
        save_dir = os.path.join("documents", utente, cliente_selezionato)
        os.makedirs(save_dir, exist_ok=True)

        filename = uploaded_file.name
        if tag:
            name_parts = os.path.splitext(filename)
            filename = f"{name_parts[0]}_{tag}{name_parts[1]}"

        file_path = os.path.join(save_dir, filename)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ File '{filename}' salvato correttamente.")

    # === VISUALIZZA FILE CARICATI ===
    st.subheader("📁 Documenti già caricati")

    docs_dir = os.path.join("documents", utente, cliente_selezionato)
    if os.path.exists(docs_dir):
        files = os.listdir(docs_dir)
        if files:
            for file_name in files:
                file_path = os.path.join(docs_dir, file_name)
                col1, col2, col3 = st.columns([5, 1, 1])

                with col1:
                    if file_name.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                        st.image(file_path, width=200)
                    elif file_name.lower().endswith(".pdf"):
                        st.markdown(f"[📄 {file_name}](./{file_path})", unsafe_allow_html=True)
                    else:
                        st.write(f"📄 {file_name}")

                with col2:
                    with open(file_path, "rb") as f:
                        st.download_button("⬇️", data=f, file_name=file_name, mime="application/octet-stream", key=file_name)

                with col3:
                    if st.button("🗑️", key=f"delete_{file_name}"):
                        os.remove(file_path)
                        st.success(f"🗑️ File '{file_name}' eliminato.")
                        st.experimental_rerun()
        else:
            st.info("Nessun documento caricato per questo cliente.")
    else:
        st.info("Nessuna cartella trovata per questo cliente.")
