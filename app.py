import streamlit as st
from modules import (landing, dashboard, invoices, clients, usercalendar,
                     documents, email_handler, automations, taxes, diagnostics, feedback, settings)
from utils import db
import utils.auth
from utils.auth import is_authenticated, require_auth, logout_button
from modules.landing import inject_styles
from streamlit_option_menu import option_menu
from utils.logging_setup import setup_logging, get_app_logger

setup_logging()
log = get_app_logger()
log.info("app_boot")

# Config pagina
st.set_page_config(
    page_title="FAi - Freelance Dashboard",
    layout="centered",
    initial_sidebar_state="collapsed"  # Sidebar chiusa di default su mobile
)

# Se non autenticato → mostra landing e ferma esecuzione
if not is_authenticated():
    landing.show()
    st.stop()

# Utente loggato: controllo sessione valida
user = require_auth()
if not user or "id" not in user:
    st.error("⚠️ Sessione non valida. Effettua di nuovo il login.")
    st.stop()

st.sidebar.caption(f"Utente: **{user.get('name')}**  \nEmail: {user.get('email')}")
user_id = user["id"]
logout_button(location="sidebar")  # SOLO qui

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
""", unsafe_allow_html=True)

# Inizializza DB
db.init_db()

# Adotta font nostro
inject_styles()

# Inizializza session_state per la navigazione
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

# Stili personalizzati verde (solo per la parte landing/public menu)
st.markdown("""
    <style>
    .sidebar-item {
        padding: 0.75rem 1rem;
        margin: 0.3rem 0;
        border-radius: 10px;
        background-color: #f0fdf4;
        font-weight: 500;
        transition: background-color 0.3s ease;
    }
    .sidebar-item:hover {
        background-color: #bbf7d0;
        cursor: pointer;
    }
    .sidebar-selected {
        background-color: #22c55e !important;
        color: white !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Funzione di rendering del menu sidebar (landing/public)
def render_sidebar_menu(current_page):
    for key, label in pages.items():
        selected = "sidebar-selected" if current_page == key else ""
        if st.sidebar.markdown(
            f"<div class='sidebar-item {selected}' onclick='window.dispatchEvent(new CustomEvent(\"streamlit_select_page\", {{ detail: \"{key}\" }}))'>{label}</div>",
            unsafe_allow_html=True
        ):
            pass

# Listener JS per cambio pagina
st.markdown("""
    <script>
    window.addEventListener("streamlit_select_page", (event) => {
        const page = event.detail;
        const streamlitInput = window.parent.streamlitSendMessage;
        if (page && streamlitInput) {
            streamlitInput({ type: "streamlit:setComponentValue", key: "selected_page", value: page });
        }
    });
    </script>
""", unsafe_allow_html=True)

# === Utente autenticato: mostra il menu di navigazione ===
# Definizione pagine + icone per option_menu
nav_keys   = ["dashboard", "invoices", "usercalendar", "clients", "documents", "emails", "automations", "taxes", "settings", "diagnostics", "feedback"]
nav_labels = ["Dashboard", "Fatture", "Calendario", "Clienti", "Documenti", "Email", "Automazioni", "Tasse", "Impostazioni", "Diagnostica", "Feedback"]
nav_icons  = ["speedometer2", "receipt", "calendar-event", "people", "folder", "envelope", "cpu", "cash", "gear", "wrench", "chat"]

# Sidebar: logout e navigazione
with st.sidebar:
    try:
        current_index = nav_keys.index(st.session_state.page)
    except Exception:
        current_index = 0

    choice = option_menu(
        None,
        nav_labels,
        icons=nav_icons,
        menu_icon=None,
        default_index=current_index,
        orientation="vertical",
        key="nav_menu",  # <-- chiave stabile: evita il doppio click
        styles={
            "container": {"padding": "2px 4px"},
            "nav-link": {
                "padding": "6px 10px",
                "margin": "2px 0",
                "border-radius": "10px",
                "width": "100%",
                "text-align": "left",
                "font-weight": "500",
                "color": "#0f172a",  # <-- testo non selezionato
            },
            "nav-link-selected": {
                "background-color": "#f0f2f6",
                "color": "#0f172a",  # <-- testo selezionato leggibile
            },
            "icon": {"color": "#334155"},  # <-- icona non selezionata
            "icon_selected": {"color": "#0f172a"},
        },
    )

    if choice in nav_labels:
        st.session_state.page = nav_keys[nav_labels.index(choice)]

# Mostra il contenuto della pagina selezionata
if st.session_state.page == "dashboard":
    dashboard.show()
elif st.session_state.page == "invoices":
    invoices.show()
elif st.session_state.page == "usercalendar":
    usercalendar.show()
elif st.session_state.page == "clients":
    clients.show()
elif st.session_state.page == "documents":
    documents.show()
elif st.session_state.page == "emails":
    email_handler.show()
elif st.session_state.page == "automations":
    automations.show()
elif st.session_state.page == "taxes":
    taxes.show()
elif st.session_state.page == "settings":
    settings.show()
elif st.session_state.page == "feedback":
    feedback.show()
elif st.session_state.page == "diagnostics":
    import modules.diagnostics as diagnostics
    diagnostics.show()
else:
    st.warning("Pagina non trovata.")
