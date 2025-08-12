import streamlit as st
from utils import db
import datetime as _dt
import re
import csv
import io
from utils import db
from collections import defaultdict

def export_clients_to_csv(user_id: int):
    clienti = db.lista_clienti_by_user_id(user_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Nome", "Email", "PEC", "Telefono", "Indirizzo", "PIVA", "CF", "Note"])
    for c in clienti:
        writer.writerow([
            c["nome"], c["email"], c["pec"], c["telefono"],
            c["indirizzo"], c["piva"], c["cf"], c["note"]
        ])
    return output.getvalue()


def import_clients_from_csv(file, user_id: int):
    text = io.StringIO(file.getvalue().decode("utf-8"))
    reader = csv.DictReader(text)
    count = 0
    for row in reader:
        nome = (row.get("Nome") or "").strip()
        email = (row.get("Email") or "").strip()
        if not nome or not email or "@" not in email:
            continue  # skip righe non valide
        db.aggiungi_cliente(
            nome, email,
            row.get("PEC"), row.get("Telefono"), row.get("Indirizzo"),
            row.get("PIVA"), row.get("CF"), row.get("Note"),
            user_id=user_id
        )
        count += 1
    return count


def is_email(s: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", (s or "").strip()))

def show():
    if "user" not in st.session_state:
        st.warning("⚠️ Effettua il login per accedere.")
        return

    user = st.session_state["user"]
    user_id = user["id"]

    st.title("👥 Clienti")

    # === Modifica cliente via query param ?id=...
    id_modifica = None
    cliente_esistente = None
    if "id" in st.query_params:
        try:
            id_modifica = int(st.query_params["id"])
            cliente_esistente = db.get_cliente_by_id(id_modifica)
        except Exception:
            id_modifica = None

    # === Form nuovo/aggiorna cliente ===
    with st.form("form_cliente"):
        id_cliente = st.text_input(
            "ID Cliente (lascia vuoto per nuovo)",
            value=str(cliente_esistente["id"]) if cliente_esistente else ""
        )
        nome = st.text_input(
            "Nome completo",
            value=cliente_esistente["nome"] if cliente_esistente else "",
            placeholder="Es. Mario Rossi SRL"
        )
        email = st.text_input(
            "Email",
            value=cliente_esistente["email"] if cliente_esistente else "",
            placeholder="esempio@azienda.it"
        )
        pec = st.text_input(
            "PEC",
            value=cliente_esistente["pec"] if cliente_esistente else "",
            placeholder="mario.rossi@pec.it"
        )
        telefono = st.text_input(
            "Telefono",
            value=cliente_esistente["telefono"] if cliente_esistente else ""
        )
        indirizzo = st.text_input(
            "Indirizzo",
            value=cliente_esistente["indirizzo"] if cliente_esistente else "",
            placeholder="Via Roma 1, 00100 Roma (RM)"
        )
        piva = st.text_input(
            "Partita IVA",
            value=cliente_esistente["piva"] if cliente_esistente else "",
            placeholder="IT01234567890"
        )
        cf = st.text_input(
            "Codice Fiscale",
            value=cliente_esistente["cf"] if cliente_esistente else "",
            placeholder="RSSMRA85M01H501Z"
        )
        note = st.text_input(
            "Note",
            value=cliente_esistente["note"] if cliente_esistente else "",
            placeholder="Annotazioni interne..."
        )

        submitted = st.form_submit_button("💾 Salva Cliente")
        if submitted:
            problems = []
            if not (nome or "").strip():
                problems.append("Il nome cliente è obbligatorio.")
            if email and not is_email(email):
                problems.append("Email non valida.")
            if pec and not is_email(pec):
                problems.append("PEC non valida.")
            if problems:
                for p in problems:
                    st.warning(f"• {p}")
                st.stop()

            if (id_cliente or "").strip():
                try:
                    _id = int(id_cliente)
                except Exception:
                    st.error("ID cliente non valido.")
                    st.stop()
                db.update_cliente(_id, nome, email, pec, telefono, indirizzo, piva, cf, note)
                st.success("✅ Cliente aggiornato.")
            else:
                db.aggiungi_cliente(
                    nome, email, pec, telefono, indirizzo, piva, cf, note,
                    utente=user["email"], user_id=user_id
                )
                st.success("✅ Cliente aggiunto.")

            st.query_params.clear()
            st.rerun()

    st.divider()
    st.subheader("📤 Esporta / 📥 Importa Clienti")

    # Export CSV
    csv_data = export_clients_to_csv(user_id)
    st.download_button(
        label="📤 Esporta CSV",
        data=csv_data,
        file_name="clienti_export.csv",
        mime="text/csv"
    )

    # Import CSV
    uploaded_file = st.file_uploader("📥 Importa CSV Clienti", type=["csv"])
    if uploaded_file:
        imported_count = import_clients_from_csv(uploaded_file, user_id)
        st.success(f"✅ Importati {imported_count} clienti validi")

    st.divider()

    # === Barra azioni: ricerca, filtro, ordinamento
    with st.container():
        c1, c2, c3 = st.columns([2, 1.4, 1.6])
        query = c1.text_input("🔎 Cerca", value="", placeholder="Es. Mario Rossi SRL o mario@azienda.it")
        filtro = c2.selectbox("Filtro", ["Tutti", "Con fatture ultimo anno", "Senza fatture"])
        sortopt = c3.selectbox("Ordina per", ["Nome (A→Z)", "Ultima fattura (recente→vecchio)"])
    # === Dataset clienti + mappa fatture
    clienti = db.lista_clienti_by_user_id(user_id)
    fatture = db.get_all_invoices_by_user_id(user_id)

    st.divider()

    # helper per compatibilità (dict o tuple)
    def _get(row, key, idx=None):
        if isinstance(row, dict):
            return row.get(key)
        return row[idx] if idx is not None else None

    def _parse_date(s):
        try:
            return _dt.date.fromisoformat(str(s))
        except Exception:
            return None

    last_by_client = {}
    count_last_year = {}
    one_year_ago = _dt.date.today() - _dt.timedelta(days=365)

    for f in fatture:
        cli = _get(f, "cliente", 2)
        d = _parse_date(_get(f, "data", 5))
        if not d or not cli:
            continue
        if cli not in last_by_client or d > last_by_client[cli]:
            last_by_client[cli] = d
        if d >= one_year_ago:
            count_last_year[cli] = count_last_year.get(cli, 0) + 1

    # === Ricerca
    if query:
        q = query.lower().strip()
        clienti = [c for c in clienti if q in (c["nome"] or "").lower() or q in (c["email"] or "").lower()]

    # === Filtro
    if filtro == "Con fatture ultimo anno":
        clienti = [c for c in clienti if count_last_year.get(c["nome"], 0) > 0]
    elif filtro == "Senza fatture":
        clienti = [c for c in clienti if count_last_year.get(c["nome"], 0) == 0]

    # === Arricchisci meta
    for c in clienti:
        c["_ultima_fattura"] = last_by_client.get(c["nome"])
        c["_fatture_12m"] = count_last_year.get(c["nome"], 0)

    # === Ordinamento
    if sortopt == "Nome (A→Z)":
        clienti.sort(key=lambda x: (x["nome"] or "").lower())
    else:
        clienti.sort(key=lambda x: x["_ultima_fattura"] or _dt.date(1900, 1, 1), reverse=True)

    # === Rendering elenco
    for c in clienti:
        riga = f"**{c['nome']}** — {c['email'] or '—'}"
        sub = []
        if c["_ultima_fattura"]:
            sub.append(f"ultima fattura: {c['_ultima_fattura'].isoformat()}")
        sub.append(f"fatture 12 mesi: {c['_fatture_12m']}")
        st.markdown(f"- {riga}  \n  <span style='color:#64748b'>{' • '.join(sub)}</span>", unsafe_allow_html=True)

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
            fatt_cli = db.get_invoices_by_client_and_user_id(c['nome'], user_id) if hasattr(db, "get_invoices_by_client_and_user_id") else []
            if fatt_cli:
                with st.expander("📄 Fatture collegate"):
                    # fatt_cli presumibilmente è una lista di tuple
                    for f in fatt_cli:
                        num = f[1]; data = f[5]; tot = f[7]
                        st.markdown(f"- Fattura **n. {num}** del {data} — €{tot:.2f}")
            else:
                st.info("Nessuna fattura collegata.")
