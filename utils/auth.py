# auth.py — login/registrazione in landing + SQLite + bcrypt + sessione
import sqlite3
import time
import pathlib
from pathlib import Path
from typing import Optional, Dict
import streamlit as st
import bcrypt
import utils.db
from utils import db
from utils.db import get_user_by_email, init_users_table, create_user

# =========================
# Config
# =========================
BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = str(BASE_DIR / "data" / "fatture.db")

SESSION_TTL = 60 * 60 * 8  # 8 ore
ALLOW_SELF_SIGNUP = False  # False per i primi tester (crei tu gli account)

# =========================
# Core API
# =========================
def verify_login(email: str, password: str):
    """Verifica le credenziali e restituisce il dict utente completo se valide, altrimenti None."""
    if not email or not password:
        return None

    norm = (email or "").strip().lower()
    user = get_user_by_email(norm)
    if not user:
        return None

    stored_hash = user.get("password_hash")
    if not stored_hash:
        return None

    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode()

    try:
        if bcrypt.checkpw(password.encode(), stored_hash):
            return user
    except ValueError:
        return None

    return None
# --- Just for TESTING
def check_credentials(email: str, password: str) -> bool:
    """Verifica credenziali email/password."""
    user = db.get_user_by_email(email)
    if not user:
        return False
    stored_hash = user.get("password_hash")
    if not stored_hash:
        return False
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode("utf-8")
    return bcrypt.checkpw(password.encode("utf-8"), stored_hash)


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
    """Garantisce che esista st.session_state['user'] con id/email/name."""
    if "user" in st.session_state and isinstance(st.session_state["user"], dict):
        if "id" in st.session_state["user"]:
            return st.session_state["user"]

    # compat con vecchio 'utente'
    email = st.session_state.get("utente")
    if email:
        uid = get_user_id_by_email(email)
        if uid:
            st.session_state["user"] = {
                "id": uid,
                "email": email,
                "name": email
            }
            return st.session_state["user"]

    st.stop()


def logout_button(location: str = "sidebar"):
    area = st.sidebar if location == "sidebar" else st
    if area.button("🚪 Esci", key=f"logout_{location}"):
        st.session_state.clear()
        st.rerun()

# =========================
# UI blocks per la landing
# =========================
def login_form():
    st.subheader("🔐 Login")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Accedi")

    if submit:
        if not email or not password:
            st.warning("Inserisci email e password.")
            st.stop()

        user_data = verify_login(email, password)
        if user_data:
            st.session_state["user"] = {
                "id": user_data["id"],
                "email": user_data["email"],
                "name": user_data.get("display_name") or user_data["email"]
            }
            # compat: mantieni 'utente' finché non rimuovi tutte le vecchie chiamate
            st.session_state["utente"] = user_data["email"]

            st.success("✅ Login effettuato!")
            st.rerun()
        else:
            st.error("❌ Credenziali non valide.")

def registration_form():
    st.subheader("📝 Registrazione")

    with st.form("registration_form"):
        display_name = st.text_input("Nome visualizzato")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Conferma Password", type="password")
        submit = st.form_submit_button("Registrati")

    if submit:
        if not display_name or not email or not password or not confirm_password:
            st.warning("Compila tutti i campi.")
            st.stop()

        if password != confirm_password:
            st.error("Le password non coincidono.")
            st.stop()

        if get_user_by_email(email):
            st.error("Email già registrata.")
            st.stop()

        # Hash della password
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        # Crea utente e recupera ID
        user_id = create_user(email, hashed_pw, display_name)

        if user_id:
            # Metti subito in sessione
            st.session_state["user"] = {
                "id": user_id,
                "email": email,
                "name": display_name
            }
            st.session_state["utente"] = email  # compat temporanea

            st.success("✅ Registrazione completata!")
            st.experimental_rerun()
        else:
            st.error("Errore durante la registrazione. Riprova.")

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
