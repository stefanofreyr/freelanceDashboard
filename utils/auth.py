import streamlit as st
from modules.landing import inject_styles


# ⚠️ Placeholder users dictionary (da sostituire con DB)
USERS = {
    "giuseppe": {"password": "1234", "nome": "Giuseppe"},
    "maria": {"password": "abcd", "nome": "Maria"},
}


def login_form():
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Accedi"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state["utente"] = USERS[username]["nome"]
            st.success(f"Benvenuto, {USERS[username]['nome']}!")
            st.rerun()
        else:
            st.error("Credenziali errate.")


def registration_form():
    st.subheader("🆕 Registrazione (demo)")
    new_username = st.text_input("Nuovo Username")
    new_password = st.text_input("Nuova Password", type="password")
    if st.button("Registrati"):
        if new_username in USERS:
            st.warning("Utente già esistente.")
        else:
            USERS[new_username] = {"password": new_password, "nome": new_username.capitalize()}
            st.success("Registrazione avvenuta. Ora effettua il login.")


def logout_button():
    if st.sidebar.button("🚪 Logout"):
        st.session_state.pop("utente", None)
        st.rerun()
