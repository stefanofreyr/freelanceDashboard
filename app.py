import streamlit as st
#from modules import dashboard, invoices, calendar, email_handler, clients, automations
from modules import invoices
from utils import db

db.init_db()

st.set_page_config(page_title="Gestione Fatture", layout="centered")

st.sidebar.title("📚 Menu")
"""
menu = st.sidebar.radio("Vai a", ["Dashboard", "Fatture", "Calendario", "Email", "Clienti", "Automazioni"])

if menu == "Dashboard":
    dashboard.show()
elif menu == "Fatture":
    invoices.show()
elif menu == "Calendario":
    calendar.show()
elif menu == "Email":
    email_handler.show()
elif menu == "Clienti":
    clients.show()
elif menu == "Automazioni":
    automations.show()

FOR LATER, WHEN THE OTHER SECTIONS ARE READY
"""
st.set_page_config(page_title="Gestione Fatture", layout="centered")
st.sidebar.title("Menu")
page = st.sidebar.radio("Navigazione", ["Fatture"])

if page == "Fatture":
    invoices.show()
