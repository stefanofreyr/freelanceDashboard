import streamlit as st
from modules import landing, dashboard, invoices, clients, calendar  # puoi aggiungere qui anche altri moduli
from utils import db, auth
from modules.landing import inject_styles

# Inizializza DB
db.init_db()

# Adotta font nostro
inject_styles()

# Aggiorna SQL file con colonna utente
db.patch_clienti_add_utente_column()
db.patch_invoices_add_utente_column()
db.patch_eventi_add_utente_column()

# Config pagina
st.set_page_config(page_title="Gestione Fatture", layout="wide")

# Logo
# st.logo("static/logo.png", link="https://yourwebsite.com")

# Sidebar navigation - modify as more sections are added, by adding them to the list []
# Se utente NON loggato, mostra landing + login
if "utente" not in st.session_state:
    # === Landing Page pubblica ===
    landing.show()

    # === Sidebar per login/registrazione ===
    st.sidebar.title("👋 Benvenuto su FAi")
    menu = st.sidebar.radio("Accedi a:", ["Login", "Registrazione"])
    if menu == "Login":
        auth.login_form()
    else:
        auth.registration_form()

else:
    # === Sidebar dopo login ===
    auth.logout_button()
    st.sidebar.markdown(f"✅ Utente: **{st.session_state['utente']}**")
    page = st.sidebar.radio("Navigazione", ["🏠 Dashboard", "📄 Fatture", "📅 Calendario", "👥 Clienti"])

    if page == "🏠 Dashboard":
        dashboard.show()
    elif page == "📄 Fatture":
        invoices.show()
    elif page == "📅 Calendario":
        calendar.show()
    elif page == "👥 Clienti":
        clients.show()
