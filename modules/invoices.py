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

        st.markdown(f"**Totale con IVA:** € {totale:.2f}")

        submitted = st.form_submit_button("Salva Fattura")
        if submitted:
            db.insert_invoice(cliente, descrizione, importo, str(data), iva, totale)
            st.success("✅ Fattura salvata!")

    st.divider()
    st.subheader("📁 Archivio Fatture")
    fatture = db.get_all_invoices()

    if fatture:
        for f in fatture:       # shows archived invoices
            fattura = {
                'id': f[0],
                'cliente': f[1],
                'descrizione': f[2],
                'importo': f[3],
                'data': f[4],
                'iva': f[5],
                'totale': f[6]
            }
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(
                    f"**{fattura['cliente']}** - {fattura['descrizione']} | €{fattura['importo']} + {fattura['iva']}% → **€{fattura['totale']}** ({fattura['data']})")
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

    else:
        st.info("Nessuna fattura salvata.")     # when there are no invoices
