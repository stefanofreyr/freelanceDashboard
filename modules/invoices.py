import streamlit as st
from utils import db
import datetime
import os
import re
from utils.pdf_generator import generate_invoice_pdf
from utils.fatturapa_generator import generate_fattura_xml
from utils.sdi_sender import send_via_pec
from utils.email_utils import send_invoice_email
from modules.landing import inject_styles
from utils.email_utils import is_test_mode

def show():
    def is_email(s: str) -> bool:
        return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", (s or "").strip()))

    if is_test_mode():
        st.info("🧪 Modalità test attiva: gli invii email/PEC sono solo simulati.")

    if "user" not in st.session_state:
        st.error("⚠️ Devi effettuare il login per accedere a questa sezione.")
        return
    user = st.session_state["user"]
    user_id = user["id"]
    utente = user["email"]

    inject_styles()
    # === CREDENZIALI PEC ===
    test_mode = st.sidebar.checkbox("🧪 Modalità Test (sandbox)", value=True)
    st.sidebar.markdown("### ✉️ PEC")

    # Default da secrets (senza cambiare la logica esistente)
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

    with st.form("fattura_form"):
        cliente = st.text_input("👤 Cliente")
        descrizione = st.text_area("🧾 Descrizione Servizio")
        importo = st.number_input("💰 Importo (€)", min_value=0.0, format="%.2f")
        data = st.date_input("📅 Data", value=datetime.date.today())
        iva = st.number_input("🧾 IVA (%)", min_value=0.0, max_value=100.0, value=iva_default, step=0.5)
        totale = importo * (1 + iva / 100)
        email_cliente = st.text_input("📧 Email Cliente")

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
            numero = db.get_next_invoice_number_for_year_by_user_id(user_id, anno)  # 👈 versione user_id
            db.insert_invoice(
                numero, cliente, descrizione, importo, str(data), iva, totale, email_cliente,
                utente=user["email"], user_id=user_id, anno=anno
            )
            st.success("✅ Fattura salvata!")

    st.markdown("<div class='section-title'>📁 Archivio Fatture</div>", unsafe_allow_html=True)

    fatture = db.get_all_invoices_by_user_id(user_id)

    if fatture:
        for f in fatture:
            if not isinstance(f, (list, tuple)) or len(f) < 9:
                st.warning("⚠️ Fattura malformata ignorata.")
                continue

            fattura = {
                'id': f[0],
                'numero_fattura': f[1],
                'cliente': f[2],
                'descrizione': f[3],
                'importo': f[4],
                'data': f[5],
                'iva': f[6],
                'totale': f[7],
                'email': f[8]
            }

            with st.container():
                st.markdown('<div class="invoice-card">', unsafe_allow_html=True)
                st.markdown(
                    f"**Fattura {fattura['numero_fattura']}**<br>"
                    f"{fattura['cliente']} — <i>{fattura['descrizione']}</i><br>"
                    f"<b>Totale:</b> €{fattura['totale']:.2f} | <b>Data:</b> {fattura['data']}",
                    unsafe_allow_html=True
                )

                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button(f"📄 PDF", key=f"pdf_{f[0]}"):
                        pdf_path = generate_invoice_pdf(fattura)
                        with open(pdf_path, "rb") as fpdf:
                            st.download_button(
                                label="Scarica PDF",
                                data=fpdf,
                                file_name=os.path.basename(pdf_path),
                                mime="application/pdf",
                                key=f"dl_{f[0]}"
                            )

                with col2:
                    if st.button(f"📧 Invia Email", key=f"email_{f[0]}"):
                        subject = f"Fattura n. {fattura['numero_fattura']}"
                        body = f"Ciao {fattura['cliente']},\n\nIn allegato trovi la tua fattura.\nGrazie!"
                        pdf_path = generate_invoice_pdf(fattura)
                        success = send_invoice_email(fattura['email'], subject, body, pdf_path)
                        if success:
                            st.success("✅ Email inviata!")
                        else:
                            st.error("❌ Errore nell'invio.")

                with col3:
                    if st.button(f"📤 PA", key=f"sdi_{f[0]}"):
                        xml_path = generate_fattura_xml(fattura)
                        if not pec_email or not pec_password:
                            st.error("❌ Inserisci credenziali PEC nella sidebar.")
                        else:
                            if test_mode:
                                st.info(
                                    f"🧪 [Modalità Test] Fattura {fattura['numero_fattura']} simulata. Nessuna PEC inviata.")
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
                                    with open("logs/pec_log.txt", "a") as log:
                                        log.write(
                                            f"Fattura {fattura['numero_fattura']} inviata via PEC a SDI ({fattura['data']})\n")
                                else:
                                    st.error(msg)

                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("🔍 Nessuna fattura salvata.")

    # === MOSTRA LOG PEC ===
    st.markdown("<div class='section-title'>📒 Log Invii PEC</div>", unsafe_allow_html=True)
    log_path = "logs/pec_log.txt"
    if os.path.exists(log_path):
        with open(log_path, "r") as log_file:
            log_content = log_file.read()
        st.text_area("Log PEC", log_content, height=150)

        if st.button("🗑️ Cancella log PEC"):
            os.remove(log_path)
            st.success("Log PEC cancellato.")
    else:
        st.info("Nessun invio PEC registrato.")
