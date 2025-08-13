import streamlit as st
from utils import db
import datetime
from calendar import monthrange
from modules.landing import inject_styles

def show():
    if "user" not in st.session_state:
        st.error("⚠️ Devi effettuare il login per accedere a questa sezione.")
        return
    user = st.session_state["user"]
    user_id = user["id"]
    utente = user["email"]

    st.title("📅 Calendario Eventi")

    inject_styles()
    st.subheader("➕ Aggiungi Nuovo Evento")
    with st.form("form_evento"):
        titolo = st.text_input("Titolo")
        data = st.date_input("Data", min_value=datetime.date.today())
        ora = st.time_input("Ora")
        clienti = db.lista_clienti(utente)
        cliente = st.selectbox("Cliente (opzionale)", [""] + [c["nome"] for c in clienti])
        descrizione = st.text_area("Descrizione")

        submitted = st.form_submit_button("Salva Evento")
        if submitted:
            db.aggiungi_evento(titolo, str(data), ora, cliente, descrizione, utente=utente, user_id=user_id)
            st.success("✅ Evento salvato!")

    st.divider()
    eventi = db.lista_eventi_futuri_by_user_id(user_id)
    oggi = datetime.date.today()

    vista = st.radio("🖥️ Seleziona visualizzazione calendario:", ["Vista Settimanale", "Vista Mensile"], horizontal=True)

    # === VISTA SETTIMANALE ===
    if vista == "Vista Settimanale":
        st.subheader("🗓️ Vista Settimanale")
        prossima_settimana = oggi + datetime.timedelta(days=7)
        eventi_settimana = [e for e in eventi if oggi <= datetime.date.fromisoformat(e["data"]) <= prossima_settimana]

        if eventi_settimana:
            oggi = datetime.date.today()
            inizio_settimana = oggi - datetime.timedelta(days=oggi.weekday())
            giorni_settimana = {}
            for i in range(7):
                giorno = inizio_settimana + datetime.timedelta(days=i)
                giorni_settimana[giorno] = db.get_eventi_per_data(utente, str(giorno))

            for giorno, eventi_giorno in giorni_settimana.items():
                st.markdown(f"### {giorno.strftime('%A %d/%m/%Y')}")
                if eventi_giorno:
                    for e in sorted(eventi_giorno, key=lambda x: x["ora"]):
                        st.markdown(f"- ⏰ **{e['ora']}** — **{e['titolo']}**")
                        if e["cliente"]:
                            st.markdown(f"  👤 Cliente: {e['cliente']}")
                        if e["descrizione"]:
                            st.markdown(f"  📝 {e['descrizione']}")

                        col_mod, col_del = st.columns(2)
                        with col_mod:
                            if st.button("✏️ Modifica", key=f"edit_{e['id']}"):
                                with st.form(f"edit_form_{e['id']}"):
                                    new_titolo = st.text_input("Titolo", e["titolo"])
                                    new_data = st.date_input("Data", datetime.date.fromisoformat(e["data"]))
                                    new_ora = st.time_input("Ora", datetime.datetime.strptime(e["ora"], "%H:%M").time())
                                    clienti = db.lista_clienti(utente)
                                    new_cliente = st.selectbox(
                                        "Cliente (opzionale)",
                                        [""] + [c["nome"] for c in clienti],
                                        index=([""] + [c["nome"] for c in clienti]).index(e["cliente"] or "")
                                    )
                                    new_descrizione = st.text_area("Descrizione", e["descrizione"] or "")
                                    if st.form_submit_button("Salva modifiche"):
                                        db.update_evento(e["id"], new_titolo, new_data, new_ora, new_cliente,
                                                         new_descrizione)
                                        st.success("✅ Evento aggiornato!")
                                        st.rerun()
                        with col_del:
                            if st.button("🗑️ Elimina", key=f"del_{e['id']}"):
                                db.elimina_evento(e["id"])
                                st.warning("❌ Evento eliminato!")
                                st.rerun()

        else:
            st.info("Nessun evento previsto per i prossimi 7 giorni.")

    # === VISTA MENSILE ===
    # === VISTA MENSILE ===
    elif vista == "Vista Mensile":
        st.subheader("📅 Vista Mensile")
        col1, col2 = st.columns(2)
        with col1:
            anno = st.selectbox("Anno", options=[oggi.year, oggi.year + 1], index=0)
        with col2:
            mese = st.selectbox(
                "Mese",
                options=list(range(1, 13)),
                format_func=lambda m: datetime.date(1900, m, 1).strftime('%B')
            )

        num_giorni = monthrange(anno, mese)[1]
        giorni_eventi = {}

        for e in eventi:
            data_evento = datetime.date.fromisoformat(e["data"])
            if data_evento.year == anno and data_evento.month == mese:
                giorno = data_evento.day
                giorni_eventi.setdefault(giorno, []).append(e)

        for giorno in range(1, num_giorni + 1):
            label = datetime.date(anno, mese, giorno).strftime("%A %d/%m")
            if giorno in giorni_eventi:
                with st.expander(f"📆 {label} ({len(giorni_eventi[giorno])} evento/i)"):
                    for ev in sorted(giorni_eventi[giorno], key=lambda x: x["ora"]):
                        st.markdown(f"- ⏰ **{ev['ora']}** — **{ev['titolo']}**")
                        if ev["cliente"]:
                            st.markdown(f"  👤 Cliente: {ev['cliente']}")
                        if ev["descrizione"]:
                            st.markdown(f"  📝 {ev['descrizione']}")

                        col_mod, col_del = st.columns(2)
                        with col_mod:
                            if st.button("✏️ Modifica", key=f"edit_mensile_{ev['id']}"):
                                with st.form(f"edit_form_mensile_{ev['id']}"):
                                    new_titolo = st.text_input("Titolo", ev["titolo"])
                                    new_data = st.date_input("Data", datetime.date.fromisoformat(ev["data"]))
                                    new_ora = st.time_input("Ora",
                                                            datetime.datetime.strptime(ev["ora"], "%H:%M").time())
                                    clienti = db.lista_clienti(utente)
                                    new_cliente = st.selectbox(
                                        "Cliente (opzionale)",
                                        [""] + [c["nome"] for c in clienti],
                                        index=([""] + [c["nome"] for c in clienti]).index(ev["cliente"] or "")
                                    )
                                    new_descrizione = st.text_area("Descrizione", ev["descrizione"] or "")
                                    if st.form_submit_button("Salva modifiche"):
                                        db.update_evento(ev["id"], new_titolo, new_data, new_ora, new_cliente,
                                                         new_descrizione)
                                        st.success("✅ Evento aggiornato!")
                                        st.rerun()
                        with col_del:
                            if st.button("🗑️ Elimina", key=f"del_mensile_{ev['id']}"):
                                db.elimina_evento(ev["id"])
                                st.warning("❌ Evento eliminato!")
                                st.rerun()
            else:
                st.markdown(f"📅 {label} – Nessun evento")


    # === PROMEMORIA AUTOMATICI (sidebar) ===
    st.sidebar.markdown("### 🔔 Reminder")
    if st.sidebar.button("📤 Invia promemoria ai clienti per eventi di domani"):
        eventi = db.eventi_in_scadenza(utente)
        if not eventi:
            st.sidebar.info("Nessun evento per domani.")
        else:
            clienti = db.lista_clienti(utente)
            client_map = {c["nome"]: c["email"] for c in clienti if c["email"]}

            inviati = 0
            for e in eventi:
                email_cliente = client_map.get(e["cliente"])
                if email_cliente:
                    subject = f"⏰ Promemoria: {e['titolo']} domani alle {e['ora']}"
                    body = f"""
    Ciao {e['cliente']},

    Ti ricordiamo che domani alle {e['ora']} è previsto:

    📅 {e['titolo']}
    📝 {e['descrizione']}

    A presto!
    – FAi
    """
                    send_invoice_email(email_cliente, subject, body)
                    inviati += 1

            if inviati:
                st.sidebar.success(f"{inviati} promemoria inviati ai clienti.")
            else:
                st.sidebar.warning("Nessun cliente con email disponibile.")
