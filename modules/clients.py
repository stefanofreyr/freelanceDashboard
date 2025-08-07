import streamlit as st
from utils import db
from modules.landing import inject_styles

def show():
    if "utente" not in st.session_state:
        st.error("⚠️ Devi effettuare il login per accedere a questa sezione.")
        return
    utente = st.session_state["utente"]

    inject_styles()
    st.title("👥 Gestione Clienti")

    st.markdown("### ➕ Aggiungi o Modifica Cliente")

    with st.form("form_cliente"):
        id_cliente = st.text_input("ID Cliente (lascia vuoto per nuovo)")
        nome = st.text_input("Nome completo")
        email = st.text_input("Email")
        piva = st.text_input("Partita IVA")
        indirizzo = st.text_input("Indirizzo")
        pec = st.text_input("Email PEC")
        telefono = st.text_input("Telefono")

        submitted = st.form_submit_button("💾 Salva Cliente")
        if submitted:
            if id_cliente:
                db.update_cliente(id_cliente, nome, email, piva, indirizzo, pec, telefono, utente)
                st.success("Cliente aggiornato.")
            else:
                db.inserisci_cliente(nome, email, piva, indirizzo, pec, telefono, utente)
                st.success("Cliente aggiunto con successo.")

    st.markdown("---")
    st.markdown("### 🔍 Cerca Cliente")
    search_query = st.text_input("Cerca per nome, email o P.IVA")

    st.markdown("### 📋 Elenco Clienti Raggruppati per Lettera")

    clienti_raggruppati = db.lista_clienti_raggruppati(utente)
    if clienti_raggruppati:
        for iniziale in sorted(clienti_raggruppati.keys()):
            filtered = [c for c in clienti_raggruppati[iniziale] if search_query.lower() in c['nome'].lower() or search_query.lower() in c['email'].lower() or search_query.lower() in c['piva'].lower()]
            if filtered:
                with st.expander(f"📁 {iniziale}"):
                    for c in filtered:
                        with st.container():
                            st.markdown(f"**{c['nome']}** ({c['email']})")
                            st.markdown(f"- P.IVA: {c['piva']}")
                            st.markdown(f"- Indirizzo: {c['indirizzo']}")
                            st.markdown(f"- PEC: {c['pec']}")
                            st.markdown(f"- Telefono: {c['telefono']}")

                            # Fatture associate
                            fatture = db.fatture_per_cliente(c['nome'])
                            if fatture:
                                st.markdown("**📄 Fatture emesse:**")
                                for f in fatture:
                                    numero, data, totale = f
                                    st.markdown(f"- [Fattura n. {numero} del {data} — €{totale:.2f}](#fattura_{numero})")
                            else:
                                st.markdown("*Nessuna fattura registrata.*")

                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("✏️ Modifica", key=f"mod_{c['id']}"):
                                    st.experimental_set_query_params(id=c['id'])
                                    st.rerun()
                            with col2:
                                if st.button("🗑️ Elimina", key=f"del_{c['id']}"):
                                    db.elimina_cliente(c['id'])
                                    st.warning("Cliente eliminato.")
                                    st.rerun()
    else:
        st.info("Nessun cliente registrato.")
