import streamlit as st
from modules import landing, invoices  # puoi aggiungere qui anche altri moduli
from utils import db

# Inizializza DB
db.init_db()
db.patch_invoices_with_missing_fields()

# Config pagina
st.set_page_config(page_title="Gestione Fatture", layout="wide")

# Logo
st.logo("static/logo.png", link="https://yourwebsite.com")

# Sidebar navigation
page = st.sidebar.radio("Navigazione", ["🏠 Home", "📄 Fatture"])

# Mostra la pagina selezionata
if page == "🏠 Home":
    landing.show()
elif page == "📄 Fatture":
    invoices.show()
