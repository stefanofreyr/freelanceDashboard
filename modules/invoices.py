# modules/invoices.py
import streamlit as st
from utils import db
import datetime
import os
from utils.pdf_generator import generate_invoice_pdf

def show():
    st.title("📄 Gestione Fatture")

    st.subheader("➕ Nuova Fattura")

    with st.form("fattura_form"):
        cliente = st.text_input("Cliente")
        descrizione = st.text_area("Descrizione Servizio")
        importo = st.number_input("Importo (€)", min_value=0.0, format="%.2f")
        data = st.date_input("Data", value=datetime.date.today())
        iva = st.number_input("IVA (%)", min_value=0.0, max_value=100.0, value=22.0)
        totale = importo * (1 + iva / 100)
        email_cliente = st.text_input("Email cliente")

        st.markdown(f"**Totale con IVA:** € {totale:.2f}")

        submitted = st.form_submit_button("Salva Fattura")
        if submitted:
            db.insert_invoice(cliente, descrizione, importo, str(data), iva, totale, email_cliente)
            st.success("✅ Fattura salvata!")

    st.divider()
    st.subheader("📁 Archivio Fatture")
    fatture = db.get_all_invoices()

    if fatture:
        for f in fatture:       # shows archived invoices
            fattura = {
                'id': f[0],
                'numero_fattura': f[1],
                'cliente': f[2],
                'descrizione': f[3],
                'importo': f[4],
                'data': f[5],
                'iva': f[6],
                'totale': f[7],
                'email_cliente': f[8]
            }

            col1, col2, col3 = st.columns([4, 1, 1])

            with col1:
                st.write(
                    f"**Fattura {fattura['numero_fattura']}** — {fattura['cliente']} | {fattura['descrizione']} "
                    f"→ €{fattura['totale']:.2f} ({fattura['data']})"
                )

            with col2:
                if st.button(f"📄 PDF", key=f"pdf_{f[0]}"):
                    pdf_path = generate_invoice_pdf(fattura)
                    with open(pdf_path, "rb") as fpdf:
                        st.download_button(
                            label="Scarica PDF",
                            data=fpdf,
                            file_name=os.path.basename(pdf_path),
                            mime="application/pdf"
                        )

            with col3:
                from utils.email_utils import send_invoice_email
                # In col2 (accanto al bottone "Scarica PDF")
                if st.button(f"📧 Invia Email", key=f"email_{f[0]}"):
                    subject = f"Fattura n. {fattura['numero_fattura']}"
                    body = f"Ciao {fattura['cliente']},\n\nIn allegato trovi la tua fattura.\nGrazie!"
                    success = send_invoice_email(fattura['email'], subject, body, pdf_path)
                    if success:
                        st.success("✅ Email inviata con successo!")
                    else:
                        st.error("❌ Errore nell'invio dell'email.")


    else:
        st.info("Nessuna fattura salvata.")     # when there are no invoices
