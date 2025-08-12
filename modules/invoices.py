import streamlit as st
from utils import db
import datetime
import os
import re
import csv, io, logging
from logging.handlers import RotatingFileHandler
from utils.pdf_generator import generate_invoice_pdf
from utils.fatturapa_generator import generate_fattura_xml
from utils.sdi_sender import send_via_pec
from utils.email_utils import send_invoice_email
from modules.landing import inject_styles
from utils.email_utils import is_test_mode

def _get_app_logger():
    logger = logging.getLogger("app")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        os.makedirs("logs", exist_ok=True)
        fh = RotatingFileHandler("logs/app.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger

def _norm_invoice(row):
    """Accetta dict (nuovo) o tuple/list (legacy) e restituisce un dict uniforme."""
    if isinstance(row, dict):
        return {
            "id": row.get("id"),
            "numero_fattura": row.get("numero_fattura"),
            "cliente": row.get("cliente"),
            "descrizione": row.get("descrizione"),
            "importo": row.get("importo"),
            "data": row.get("data"),
            "iva": row.get("iva"),
            "totale": row.get("totale"),
            "email": row.get("email"),
            "anno": row.get("anno"),
            "user_id": row.get("user_id"),
        }
    # fallback legacy: mapping per posizioni classiche
    seq = list(row)
    return {
        "id": seq[0] if len(seq) > 0 else None,
        "numero_fattura": seq[1] if len(seq) > 1 else None,
        "cliente": seq[2] if len(seq) > 2 else "",
        "descrizione": seq[3] if len(seq) > 3 else "",
        "importo": seq[4] if len(seq) > 4 else 0.0,
        "data": seq[5] if len(seq) > 5 else "",
        "iva": seq[6] if len(seq) > 6 else 0.0,
        "totale": seq[7] if len(seq) > 7 else 0.0,
        "email": seq[8] if len(seq) > 8 else "",
        "anno": seq[10] if len(seq) > 10 else None,
        "user_id": seq[9] if len(seq) > 9 else None,
    }

def _export_invoices_csv(invoices: list[dict]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID","Numero","Anno","Data","Cliente","Descrizione","Imponibile","IVA","Totale","Email"])
    for f in invoices:
        writer.writerow([
            f.get("id"),
            f.get("numero_fattura"),
            f.get("anno"),
            f.get("data"),
            f.get("cliente"),
            f.get("descrizione"),
            f.get("importo"),
            f.get("iva"),
            f.get("totale"),
            f.get("email"),
        ])
    return output.getvalue()


def show():
    logger = _get_app_logger()

    def is_email(s: str) -> bool:
        return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", (s or "").strip()))

    if is_test_mode():
        st.info("🧪 Modalità test attiva: gli invii email/PEC sono solo simulati.")

    if "user" not in st.session_state:
        st.error("⚠️ Devi effettuare il login per accedere a questa sezione.")
        return
    user = st.session_state["user"]
    user_id = user["id"]

    inject_styles()

    # === CREDENZIALI PEC ===
    test_mode = st.sidebar.checkbox("🧪 Modalità Test (sandbox)", value=True)
    st.sidebar.markdown("### ✉️ PEC")
    _pec_user_default = st.secrets.get("PEC_USER", "")
    _pec_pass_default = st.secrets.get("PEC_PASS", "")
    _provider_secret = st.secrets.get("PEC_PROVIDER", None)
    _provider_options = ["Aruba", "PosteCert", "Legalmail", "MailTrap"]
    _provider_index = _provider_options.index(_provider_secret) if _provider_secret in _provider_options else 0
    pec_email = st.sidebar.text_input("PEC Mittente", value=_pec_user_default)
    pec_password = st.sidebar.text_input("Password PEC", type="password", value=_pec_pass_default)
    pec_provider = st.sidebar.selectbox("Provider PEC", _provider_options, index=_provider_index)

    st.title("📄 Gestione Fatture")
    st.markdown("<div class='section-title'>➕ Nuova Fattura</div>", unsafe_allow_html=True)

    settings = db.get_settings(user["email"]) or {}
    iva_default = float(settings.get("iva_default") or 22.0)

    # === FORM NUOVA FATTURA ===
    with st.form("fattura_form"):
        cliente = st.text_input("👤 Cliente", placeholder="Es. Mario Rossi SRL")
        descrizione = st.text_area("🧾 Descrizione Servizio", placeholder="Consulenza sviluppo software — Sprint agosto")
        importo = st.number_input("💰 Imponibile (€)", min_value=0.0, format="%.2f")
        data = st.date_input("📅 Data", value=datetime.date.today())
        iva = st.number_input("🧾 IVA (%)", min_value=0.0, max_value=100.0, value=iva_default, step=0.5)
        totale = importo * (1 + iva / 100)
        email_cliente = st.text_input("📧 Email Cliente", placeholder="fatture@azienda.it")
        st.markdown(f"<b>Totale con IVA:</b> € {totale:.2f}", unsafe_allow_html=True)

        submit = st.form_submit_button("💾 Salva Fattura")
        if submit:
            errors = []
            if not cliente.strip():
                errors.append("Il cliente è obbligatorio.")
            if importo <= 0:
                errors.append("L'importo deve essere maggiore di 0.")
            if not (0 <= iva <= 100):
                errors.append("L'IVA deve essere tra 0 e 100.")
            if email_cliente and not is_email(email_cliente):
                errors.append("L'email cliente non è valida.")
            if errors:
                for e in errors:
                    st.warning(f"• {e}")
                st.stop()

            anno = int(str(data)[:4])
            numero = db.get_next_invoice_number_for_year_by_user_id(user_id, anno)
            db.insert_invoice(
                numero, cliente, descrizione, importo, str(data), iva, totale, email_cliente,
                utente=user["email"], user_id=user_id, anno=anno
            )

            logger.info("invoice_created user_id=%s numero=%s anno=%s cliente=%s totale=%.2f",
                        user_id, numero, anno, cliente, totale)
            st.success("✅ Fattura salvata!")

            # 📧 Email di conferma a sé stessi (SOLO fuori test)
            if not is_test_mode():
                try:
                    nuova_fattura = {
                        "id": None,
                        "numero_fattura": numero,
                        "cliente": cliente,
                        "descrizione": descrizione,
                        "importo": importo,
                        "data": str(data),
                        "iva": iva,
                        "totale": totale,
                        "email": email_cliente
                    }
                    pdf_path = generate_invoice_pdf(nuova_fattura)
                    subject = f"Conferma emissione fattura n. {numero}/{anno}"
                    who = (user.get("display_name") or user.get("email") or "").strip() or "utente"
                    body = (
                        f"Ciao {who},\n\n"
                        f"Hai emesso la fattura n. {numero}/{anno} per {cliente} il {data}.\n"
                        f"Imponibile: €{importo:.2f}  |  IVA: {iva:.1f}%  |  Totale: €{totale:.2f}\n\n"
                        f"In allegato trovi il PDF. Questo è un messaggio automatico di conferma."
                    )
                    if send_invoice_email(user["email"], subject, body, pdf_path):
                        logger.info("invoice_confirmation_email_sent user_id=%s numero=%s", user_id, numero)
                        st.toast("📧 Conferma inviata al tuo indirizzo.")
                    else:
                        logger.warning("invoice_confirmation_email_failed user_id=%s numero=%s", user_id, numero)
                        st.warning("⚠️ Non sono riuscito a inviare la conferma via email.")
                except Exception as ex:
                    logger.exception("invoice_confirmation_email_error user_id=%s numero=%s err=%s", user_id, numero, ex)
                    st.warning("⚠️ Errore durante l'invio della conferma via email.")

    # === ARCHIVIO / TOOLBAR ===
    st.markdown("<div class='section-title'>📁 Archivio Fatture</div>", unsafe_allow_html=True)
    raw = db.get_all_invoices_by_user_id(user_id) or []
    fatture = [_norm_invoice(r) for r in raw]

    # Anni disponibili (da colonna anno o da data)
    anni = []
    for f in fatture:
        y = f.get("anno")
        if not y and f.get("data"):
            try:
                y = int(str(f["data"])[:4])
            except Exception:
                y = None
        if y:
            anni.append(y)
    anni = sorted(set(anni), reverse=True)

    with st.container():
        colf1, colf2, colf3, colf4 = st.columns([2, 1, 1, 1])
        query = colf1.text_input("🔎 Cerca", placeholder="Cliente o descrizione…")
        year_opt = ["Tutti"] + [str(a) for a in anni]
        year_sel = colf2.selectbox("Anno", options=year_opt, index=0)
        # filtri
        def _match(f: dict) -> bool:
            ok = True
            if query:
                q = query.lower().strip()
                ok = q in (f.get("cliente") or "").lower() or q in (f.get("descrizione") or "").lower()
            if ok and year_sel != "Tutti":
                yy = f.get("anno")
                if not yy and f.get("data"):
                    try:
                        yy = int(str(f["data"])[:4])
                    except Exception:
                        yy = None
                ok = (str(yy) == year_sel)
            return ok

        filtered = [f for f in fatture if _match(f)]

        # metriche
        count = len(filtered)
        total = sum(float(f.get("totale") or 0.0) for f in filtered)
        colf3.metric("Fatture", count)
        colf4.metric("Totale", f"€ {total:,.2f}".replace(",", " ").replace(".", ",").replace(" ", "."))  # formato EU

        # export CSV (rispetta filtri)
        csv_data = _export_invoices_csv(filtered)
        st.download_button(
            label="📤 Esporta CSV",
            data=csv_data,
            file_name=f"fatture_{(year_sel if year_sel!='Tutti' else 'tutte')}.csv",
            mime="text/csv",
            help="Esporta le fatture filtrate"
        )

    # === LISTA (card) ===
    if filtered:
        for f in filtered:
            fattura = {
                'id': f.get('id'),
                'numero_fattura': f.get('numero_fattura'),
                'cliente': f.get('cliente'),
                'descrizione': f.get('descrizione'),
                'importo': float(f.get('importo') or 0.0),
                'data': f.get('data'),
                'iva': float(f.get('iva') or 0.0),
                'totale': float(f.get('totale') or 0.0),
                'email': f.get('email')
            }
            with st.container():
                st.markdown('<div class="invoice-card">', unsafe_allow_html=True)
                st.markdown(
                    f"**Fattura {fattura['numero_fattura']}**<br>"
                    f"{fattura['cliente']} — <i>{fattura['descrizione'] or ''}</i><br>"
                    f"<b>Totale:</b> €{fattura['totale']:.2f} | <b>Data:</b> {fattura['data']}",
                    unsafe_allow_html=True
                )
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("📄 PDF", key=f"pdf_{fattura['id']}"):
                        pdf_path = generate_invoice_pdf(fattura)
                        with open(pdf_path, "rb") as fpdf:
                            st.download_button(
                                label="Scarica PDF",
                                data=fpdf,
                                file_name=os.path.basename(pdf_path),
                                mime="application/pdf",
                                key=f"dl_{fattura['id']}"
                            )

                with col2:
                    if st.button("📧 Invia Email", key=f"email_{fattura['id']}"):
                        subject = f"Fattura n. {fattura['numero_fattura']}"
                        body = f"Ciao {fattura['cliente']},\n\nIn allegato trovi la tua fattura.\nGrazie!"
                        pdf_path = generate_invoice_pdf(fattura)
                        success = send_invoice_email(fattura['email'], subject, body, pdf_path)
                        if success:
                            st.success("✅ Email inviata!")
                        else:
                            st.error("❌ Errore nell'invio.")

                with col3:
                    if st.button("📤 PA", key=f"sdi_{fattura['id']}"):
                        xml_path = generate_fattura_xml(fattura)
                        if not pec_email or not pec_password:
                            st.error("❌ Inserisci credenziali PEC nella sidebar.")
                        else:
                            if test_mode:
                                st.info(f"🧪 [Modalità Test] Fattura {fattura['numero_fattura']} simulata. Nessuna PEC inviata.")
                            else:
                                success, msg = send_via_pec(
                                    xml_path=xml_path,
                                    mittente_pec=pec_email,
                                    mittente_password=pec_password,
                                    provider=pec_provider
                                )
                                if success:
                                    st.success(msg)
                                    os.makedirs("logs", exist_ok=True)
                                    with open("logs/pec_log.txt", "a", encoding="utf-8") as log:
                                        log.write(
                                            f"Fattura {fattura['numero_fattura']} inviata via PEC a SDI ({fattura['data']}) | utente: {user['email']}\n"
                                        )
                                else:
                                    st.error(msg)
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("🔍 Nessuna fattura trovata con i filtri correnti.")

    # === LOG PEC ===
    st.markdown("<div class='section-title'>📒 Log Invii PEC</div>", unsafe_allow_html=True)
    log_path = "logs/pec_log.txt"
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as log_file:
            log_content = log_file.read()
        st.text_area("Log PEC", log_content, height=150)
        if st.button("🗑️ Cancella log PEC"):
            os.remove(log_path)
            st.success("Log PEC cancellato.")
    else:
        st.info("Nessun invio PEC registrato.")
