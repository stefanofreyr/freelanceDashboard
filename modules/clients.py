import streamlit as st
from utils import db

def show():
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
                db.update_cliente(id_cliente, nome, email, piva, indirizzo, pec, telefono)
                st.success("Cliente aggiornato.")
            else:
                db.inserisci_cliente(nome, email, piva, indirizzo, pec, telefono)
                st.success("Cliente aggiunto con successo.")

    st.markdown("---")
    st.markdown("### 📋 Elenco Clienti")

    clienti_raggruppati = db.lista_clienti_raggruppati()
    if clienti_raggruppati:
        for iniziale in sorted(clienti_raggruppati.keys()):
            with st.expander(f"📁 {iniziale}"):
                for c in clienti_raggruppati[iniziale]:
                    with st.container():
                        st.markdown(f"**{c['nome']}** ({c['email']})")
                        st.markdown(f"- P.IVA: {c['piva']}")
                        st.markdown(f"- Indirizzo: {c['indirizzo']}")
                        st.markdown(f"- PEC: {c['pec']}")
                        st.markdown(f"- Telefono: {c['telefono']}")
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
