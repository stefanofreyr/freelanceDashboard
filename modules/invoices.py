import streamlit as st
from utils import db
import datetime
import os
from utils.pdf_generator import generate_invoice_pdf
from utils.fatturapa_generator import generate_fattura_xml
from utils.sdi_sender import send_via_pec
from utils.email_utils import send_invoice_email


def show():
    # === CREDENZIALI PEC ===
    st.sidebar.markdown("### ✉️ PEC")
    pec_email = st.sidebar.text_input("PEC Mittente")
    pec_password = st.sidebar.text_input("Password PEC", type="password")
    pec_provider = st.sidebar.selectbox("Provider PEC", ["Aruba", "PosteCert", "Legalmail"])

    st.title("📄 Gestione Fatture")

    st.markdown("<div class='section-title'>➕ Nuova Fattura</div>", unsafe_allow_html=True)

    with st.form("fattura_form"):
        cliente = st.text_input("👤 Cliente")
        descrizione = st.text_area("🧾 Descrizione Servizio")
        importo = st.number_input("💰 Importo (€)", min_value=0.0, format="%.2f")
        data = st.date_input("📅 Data", value=datetime.date.today())
        iva = st.number_input("🧾 IVA (%)", min_value=0.0, max_value=100.0, value=22.0)
        totale = importo * (1 + iva / 100)
        email_cliente = st.text_input("📧 Email Cliente")

        st.markdown(f"<b>Totale con IVA:</b> € {totale:.2f}", unsafe_allow_html=True)

        submitted = st.form_submit_button("💾 Salva Fattura")
        if submitted:
            numero = db.get_next_invoice_number()
            db.insert_invoice(numero, cliente, descrizione, importo, str(data), iva, totale, email_cliente)
            st.success("✅ Fattura salvata!")

    st.markdown("<div class='section-title'>📁 Archivio Fatture</div>", unsafe_allow_html=True)
    fatture = db.get_all_invoices()

    if fatture:
        for f in fatture:
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
                            success, msg = send_via_pec(
                                xml_path=xml_path,
                                mittente_pec=pec_email,
                                mittente_password=pec_password,
                                provider=pec_provider
                            )
                            if success:
                                st.success(msg)
                                # Salva log invio PEC
                                os.makedirs("logs", exist_ok=True)
                                with open("logs/pec_log.txt", "a") as log:
                                    log.write(f"Fattura {fattura['numero_fattura']} inviata via PEC a SDI ({fattura['data']})\n")
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

