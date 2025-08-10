# auth.py — login/registrazione in landing + SQLite + bcrypt + sessione
import sqlite3
import time
import pathlib
from typing import Optional, Dict
import streamlit as st
import bcrypt

# =========================
# Config
# =========================
DB_PATH = "data/fatture.db"
SESSION_TTL = 60 * 60 * 8  # 8 ore
ALLOW_SELF_SIGNUP = False  # False per i primi tester (crei tu gli account)

# =========================
# DB helpers
# =========================
def _conn():
    """Connessione SQLite con FK attive."""
    pathlib.Path("data").mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def _init_users_table():
    """Crea la tabella users se non esiste."""
    with _conn() as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              email TEXT NOT NULL UNIQUE,
              password_hash TEXT NOT NULL,
              display_name TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        c.commit()

# =========================
# Core API
# =========================
def create_user(email: str, password: str, display_name: str = "") -> None:
    """Crea un utente con password hashata (bcrypt)."""
    email = (email or "").strip().lower()
    if not email or not password:
        raise ValueError("Email e password sono obbligatorie")
    _init_users_table()
    ph = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with _conn() as c:
        c.execute(
            "INSERT INTO users (email, password_hash, display_name) VALUES (?, ?, ?)",
            (email, ph, (display_name or "").strip()),
        )
        c.commit()

def get_user_by_email(email: str) -> Optional[sqlite3.Row]:
    _init_users_table()
    with _conn() as c:
        return c.execute(
            "SELECT id, email, password_hash, display_name FROM users WHERE email=?",
            ((email or "").strip().lower(),),
        ).fetchone()

def verify_login(email: str, password: str) -> Optional[Dict]:
    """Ritorna un dict {id,email,name} se ok, altrimenti None."""
    row = get_user_by_email(email)
    if not row:
        return None
    ok = bcrypt.checkpw((password or "").encode(), row["password_hash"].encode())
    if not ok:
        return None
    return {
        "id": row["id"],
        "email": row["email"],
        "name": row["display_name"] or row["email"],
    }

# =========================
# Session helpers
# =========================
def is_authenticated() -> bool:
    """True se la sessione contiene un utente valido."""
    return "user" in st.session_state or "utente" in st.session_state

def current_user() -> Optional[Dict]:
    """Restituisce il dict user dalla sessione, se presente."""
    if "user" in st.session_state and st.session_state["user"]:
        return st.session_state["user"]
    # retro-compatibilità minima se altrove veniva usato solo 'utente' (stringa)
    if "utente" in st.session_state and st.session_state["utente"]:
        return {"id": None, "email": "", "name": st.session_state["utente"]}
    return None

def _touch_session():
    st.session_state["last_seen"] = int(time.time())

def require_auth():
    """
    Da usare all'inizio delle pagine *protette* (non nella landing):
    se non loggato, mostra un avviso e interrompe il rendering.
    """
    if not is_authenticated():
        st.info("Devi effettuare l’accesso per continuare.")
        st.stop()
    # timeout sessione
    now = int(time.time())
    last = st.session_state.get("last_seen", 0)
    if now - last > SESSION_TTL:
        st.session_state.clear()
        st.warning("Sessione scaduta. Accedi di nuovo.")
        st.stop()
    _touch_session()
    return current_user()

def logout_button(location: str = "sidebar"):
    """Mostra un pulsante di Logout (di default in sidebar)."""
    area = st.sidebar if location == "sidebar" else st
    if area.button("🚪 Esci"):
        st.session_state.clear()
        st.rerun()

# =========================
# UI blocks per la landing
# =========================
def login_form():
    st.markdown("#### Accedi")
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", key="login_email")
        pwd = st.text_input("Password", type="password", key="login_pwd")
        submitted = st.form_submit_button("Accedi", type="primary", use_container_width=True)
    if submitted:
        user = verify_login(email, pwd)
        if user:
            # compat: manteniamo anche 'utente' come nome visualizzato
            st.session_state["user"] = user
            st.session_state["utente"] = user["name"]
            _touch_session()
            st.success(f"Benvenuto, {user['name']}!")
            st.rerun()
        else:
            st.error("Credenziali non valide.")

def registration_form():
    st.markdown("#### Crea un nuovo account")
    with st.form("signup_form", clear_on_submit=False):
        name = st.text_input("Nome visibile (opzionale)", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        p1 = st.text_input("Password", type="password", key="signup_p1")
        p2 = st.text_input("Ripeti password", type="password", key="signup_p2")
        submitted = st.form_submit_button("Registrati", use_container_width=True)
    if submitted:
        if not email or not p1:
            st.warning("Email e password sono obbligatorie.")
            return
        if p1 != p2:
            st.warning("Le password non coincidono.")
            return
        try:
            create_user(email, p1, name)
            st.success("Account creato. Ora effettua il login.")
        except sqlite3.IntegrityError:
            st.warning("Esiste già un account con questa email.")
        except Exception as ex:
            st.error(f"Errore durante la registrazione: {ex}")

def auth_block_on_landing():
    """
    Blocco da inserire nella landing (es. modules/landing.py → show_login()).
    Mostra login; se ALLOW_SELF_SIGNUP=True, mostra anche registrazione.
    """
    st.markdown('<span id="login" class="anchor"></span>', unsafe_allow_html=True)
    st.markdown("## 🔐 Login / Registrazione")
    login_form()
    if ALLOW_SELF_SIGNUP:
        with st.expander("Non hai un account? Registrati", expanded=False):
            registration_form()
