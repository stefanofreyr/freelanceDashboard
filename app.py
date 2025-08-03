import streamlit as st
from modules import landing, invoices, clients  # puoi aggiungere qui anche altri moduli
from utils import db

# Inizializza DB
db.init_db()
db.patch_invoices_with_missing_fields()

# Config pagina
st.set_page_config(page_title="Gestione Fatture", layout="wide")

# Logo
st.logo("static/logo.png", link="https://yourwebsite.com")

# Sidebar navigation - modify as more sections are added, by adding them to the list []
page = st.sidebar.radio("Navigazione", ["🏠 Home", "📄 Fatture", "👥 Clienti"])

# Mostra la pagina selezionata - add elif statements as you create more sections
if page == "🏠 Home":
    landing.show()
elif page == "📄 Fatture":
    invoices.show()
elif page == "👥 Clienti":
    clients.show()
