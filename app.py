import streamlit as st
from modules import landing, dashboard, invoices, clients, calendar, documents, email_handler, automations, taxes
from utils import db, auth
from modules.landing import inject_styles

# Inizializza DB
db.init_db()

# Adotta font nostro
inject_styles()

# Aggiorna SQL file con colonna utente
# db.patch_clienti_add_utente_column()
# db.patch_invoices_add_utente_column()
# db.patch_eventi_add_utente_column()

# Config pagina
st.set_page_config(
    page_title="FAi - Freelance Dashboard",
    layout="centered",
    initial_sidebar_state="collapsed"  # Sidebar chiusa di default su mobile
)

# Inizializza session_state per la navigazione
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

# Lista delle pagine
pages = {
    "dashboard": "🏠 Dashboard",
    "invoices": "📄 Fatture",
    "calendar": "📅 Calendario",
    "clients": "👥 Clienti",
    "documents": "📂 Documenti"
}

# Stili personalizzati verde
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

# Funzione di rendering del menu sidebar
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

# Aggiorna pagina se cliccato
selected_page = st.query_params.get("selected_page", [None])[0]
if selected_page in pages:
    st.session_state.page = selected_page

if "utente" not in st.session_state:
    # Mostra la landing pubblica
    landing.show()

    # Inizializza stato per la pagina di login
    if "login_mode" not in st.session_state:
        st.session_state.login_mode = "login"

    # CSS per i blocchi cliccabili
    st.markdown("""
        <style>
        .auth-option {
            padding: 0.75rem 1rem;
            margin: 0.3rem 0.5rem 0.3rem 0;
            border-radius: 10px;
            background-color: #f0fdf4;
            font-weight: 500;
            display: inline-block;
            transition: background-color 0.3s ease;
        }
        .auth-option:hover {
            background-color: #bbf7d0;
            cursor: pointer;
        }
        .auth-selected {
            background-color: #22c55e !important;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Blocchi di scelta login/registrazione
    st.markdown("### Accedi a FAi")

    col1, col2 = st.columns(2)
    with col1:
        login_selected = st.session_state.login_mode == "login"
        if st.markdown(
            f"<div class='auth-option {'auth-selected' if login_selected else ''}' onclick='window.dispatchEvent(new CustomEvent(\"auth_switch\", {{ detail: \"login\" }}))'>🔐 Login</div>",
            unsafe_allow_html=True,
        ):
            pass

    with col2:
        reg_selected = st.session_state.login_mode == "registrazione"
        if st.markdown(
            f"<div class='auth-option {'auth-selected' if reg_selected else ''}' onclick='window.dispatchEvent(new CustomEvent(\"auth_switch\", {{ detail: \"registrazione\" }}))'>📝 Registrazione</div>",
            unsafe_allow_html=True,
        ):
            pass

    # JavaScript listener per cambiare modalità
    st.markdown("""
        <script>
        window.addEventListener("auth_switch", (event) => {
            const mode = event.detail;
            const streamlitInput = window.parent.streamlitSendMessage;
            if (mode && streamlitInput) {
                streamlitInput({ type: "streamlit:setComponentValue", key: "selected_auth_mode", value: mode });
            }
        });
        </script>
    """, unsafe_allow_html=True)

    # Sincronizza stato se è stato cliccato un blocco
    selected_auth_mode = st.query_params.get("selected_auth_mode", [None])[0]
    if selected_auth_mode in ["login", "registrazione"]:
        st.session_state.login_mode = selected_auth_mode

    # Mostra form corrispondente
    if st.session_state.login_mode == "login":
        auth.login_form()
    else:
        auth.registration_form()


# === Se utente loggato ===
else:
    # Inizializza pagina se non esiste
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"

    # Stile personalizzato per i pulsanti sidebar
    def sidebar_button_style(selected: bool):
        return f"""
            <style>
            div[data-testid="stButton"] > button {{
                width: 100%;
                text-align: left;
                padding: 0.75rem 1rem;
                margin: 0.3rem 0;
                border-radius: 10px;
                font-weight: 500;
                background-color: {'#22c55e' if selected else '#f0fdf4'};
                color: {'white' if selected else 'black'};
                border: none;
            }}
            div[data-testid="stButton"] > button:hover {{
                background-color: {'#16a34a' if selected else '#bbf7d0'};
                color: black;
                cursor: pointer;
            }}
            </style>
        """

    # Definisci le pagine e le etichette
    pages = {
        "dashboard": "🏠 Dashboard",
        "invoices": "📄 Fatture",
        "calendar": "📅 Calendario",
        "clients": "👥 Clienti",
        "documents": "📂 Documenti",
        "emails": "📬 Email",
        "automations": "🤖 Automazioni",
        "taxes": "💰 Tasse"
    }

    # Sidebar: logout e navigazione
    with st.sidebar:
        auth.logout_button()
        st.markdown(f"✅ Utente: **{st.session_state['utente']}**")
        st.markdown("### Navigazione")

        for key, label in pages.items():
            selected = st.session_state.page == key
            st.markdown(sidebar_button_style(selected), unsafe_allow_html=True)
            if st.button(label, key=f"nav_{key}"):
                st.session_state.page = key

    # Mostra il contenuto della pagina selezionata
    if st.session_state.page == "dashboard":
        dashboard.show()
    elif st.session_state.page == "invoices":
        invoices.show()
    elif st.session_state.page == "calendar":
        calendar.show()
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
    else:
        st.warning("Pagina non trovata.")
