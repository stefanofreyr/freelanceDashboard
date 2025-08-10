import streamlit as st
from utils import db

def show():
    user = st.session_state.get("user") or {}
    email = user.get("email")
    st.title("⚙️ Impostazioni")
    s = db.get_settings(email) or {}
    with st.form("settings"):
        rag = st.text_input("Ragione sociale", (s or {}).get("ragione_sociale") or "")
        ind = st.text_input("Indirizzo", (s or {}).get("indirizzo") or "")
        piva = st.text_input("Partita IVA", (s or {}).get("piva") or "")
        iva_def = st.number_input("IVA di default (%)", 0.0, 100.0, float((s or {}).get("iva_default") or 22.0))
        provider = st.selectbox("Provider PEC", ["Aruba","PosteCert","Legalmail","Mailtrap"], index=3)
        pec_user = st.text_input("PEC user", (s or {}).get("pec_user") or "")
        pec_pass = st.text_input("PEC password", type="password", value=(s or {}).get("pec_pass") or "")
        test_mode = st.toggle("Modalità test (non inviare davvero)", value=((s or {}).get("test_mode") or 1) == 1)
        ok = st.form_submit_button("Salva")
        if ok:
            db.upsert_settings(email,
                ragione_sociale=rag, indirizzo=ind, piva=piva, iva_default=iva_def,
                pec_provider=provider, pec_user=pec_user, pec_pass=pec_pass,
                test_mode=1 if test_mode else 0)
            st.success("Impostazioni salvate.")
