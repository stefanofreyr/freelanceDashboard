
import streamlit as st
import re
from utils import db
from collections import defaultdict

def show():
    st.title("👥 Gestione Clienti")

    def is_email(s: str) -> bool:
        return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", (s or "").strip()))


    if "user" not in st.session_state:
        st.warning("⚠️ Effettua il login per accedere.")
        return

    user = st.session_state["user"]
    user_id = user["id"]
    utente = user["email"]  # compat se stampi il nome utente

    # === Legge parametri URL per modifica ===
    id_modifica = None
    cliente_esistente = None

    if "id" in st.query_params:
        try:
            id_modifica = int(st.query_params["id"])
            cliente_esistente = db.get_cliente_by_id(id_modifica)
        except:
            id_modifica = None

    # === FORM CLIENTE ===
    with st.form("form_cliente"):
        id_cliente = st.text_input("ID Cliente (lascia vuoto per nuovo)", value=str(cliente_esistente["id"]) if cliente_esistente else "")
        nome = st.text_input("Nome completo", value=cliente_esistente["nome"] if cliente_esistente else "")
        email = st.text_input("Email", value=cliente_esistente["email"] if cliente_esistente else "")
        pec = st.text_input("PEC", value=cliente_esistente["pec"] if cliente_esistente else "")
        telefono = st.text_input("Telefono", value=cliente_esistente["telefono"] if cliente_esistente else "")
        indirizzo = st.text_input("Indirizzo", value=cliente_esistente["indirizzo"] if cliente_esistente else "")
        piva = st.text_input("Partita IVA", value=cliente_esistente["piva"] if cliente_esistente else "")
        cf = st.text_input("Codice Fiscale", value=cliente_esistente["cf"] if cliente_esistente else "")
        note = st.text_input("Note", value=cliente_esistente["note"] if cliente_esistente else "")

        submitted = st.form_submit_button("💾 Salva Cliente")
        if submitted:
            errors = []
            if not cliente.strip():
                errors.append("Il cliente è obbligatorio.")
            if importo <= 0:
                errors.append("L'importo deve essere maggiore di 0.")
            if not (0 <= iva <= 100):
                errors.append("L'IVA deve essere tra 0 e 100.")
            if email_cliente and not _is_email(email_cliente):
                errors.append("L'email cliente non è valida.")
            if errors:
                for e in errors: st.warning(f"• {e}")
                st.stop()
            if id_cliente:
                db.update_cliente(id_cliente, nome, email, pec, telefono, indirizzo, piva, cf, note)
                st.success("✅ Cliente aggiornato.")
            else:
                db.aggiungi_cliente(nome, email, pec, telefono, indirizzo, piva, cf, note, utente=user["email"], user_id=user_id)
                st.success("✅ Cliente aggiunto.")
            st.query_params.clear()
            st.rerun()

    st.divider()

    # === LISTA CLIENTI RAGGRUPPATI ===
    search_query = st.text_input("🔍 Cerca cliente per nome")
    clienti = db.lista_clienti_by_user_id(user_id)

    if search_query:
        clienti = [c for c in clienti if search_query.lower() in c["nome"].lower()]

    raggruppati = defaultdict(list)
    for c in clienti:
        iniziale = c["nome"][0].upper()
        raggruppati[iniziale].append(c)

    for iniziale in sorted(raggruppati):
        with st.expander(f"📁 {iniziale}"):
            for c in sorted(raggruppati[iniziale], key=lambda x: x["nome"]):
                st.markdown(f"**{c['nome']}** — {c['email']} — {c['telefono']}")
                col1, col2, col3 = st.columns([1, 1, 4])

                with col1:
                    if st.button("✏️", key=f"mod_{c['id']}"):
                        st.query_params.update({"id": c['id']})
                        st.rerun()

                with col2:
                    if st.button("🗑️", key=f"del_{c['id']}"):
                        db.elimina_cliente(c['id'])
                        st.success(f"🗑️ Cliente '{c['nome']}' eliminato.")
                        st.rerun()

                with col3:
                    fatture = db.get_invoices_by_client_and_user_id(c['nome'], user_id)
                    if fatture:
                        with st.expander("📄 Fatture collegate"):
                            for f in fatture:
                                st.markdown(f"- Fattura **n. {f[1]}** del {f[5]} — €{f[7]:.2f}")
                    else:
                        st.info("Nessuna fattura collegata.")
