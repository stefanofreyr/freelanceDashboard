# modules/invoices.py
import streamlit as st
from utils import db
import datetime
import os
from utils.pdf_generator import generate_invoice_pdf
from utils.fatturapa_generator import generate_fattura_xml
from utils.sdi_sender import send_via_pec

# Custom CSS
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', sans-serif;
        background-color: #f8f9fb;
    }

    h1, h2, h3, h4 {
        color: #2c3e50;
        font-weight: 600;
    }

    .invoice-card {
        background-color: white;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .section-title {
        font-size: 1.5rem;
        color: #3f51b5;
        margin-top: 2rem;
    }

    .stButton>button {
        background-color: #3f51b5;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
    }

    .stButton>button:hover {
        background-color: #303f9f;
    }

    .stDownloadButton>button {
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

def show():
    st.title("📄 Gestione Fatture")

    # === FORM NUOVA FATTURA ===
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

    # === ARCHIVIO ===
    st.markdown("<div class='section-title'>📁 Archivio Fatture</div>", unsafe_allow_html=True)
    fatture = db.get_all_invoices()

    import plotly.graph_objects as go
    from collections import defaultdict

    # === ANALISI PER GRAFICO ===
    monthly_totals_by_year = defaultdict(lambda: [0] * 12)

    for f in fatture:
        try:
            data = datetime.datetime.strptime(f[5], "%Y-%m-%d")
            year = str(data.year)
            month_index = data.month - 1
            monthly_totals_by_year[year][month_index] += f[7]
        except:
            continue  # in caso di formato data errato

    if monthly_totals_by_year:
        st.markdown("### 📊 Grafico Fatturato per Mese")
        selected_year = st.selectbox("Scegli l'anno", sorted(monthly_totals_by_year.keys(), reverse=True))

        months = [
            "Gen", "Feb", "Mar", "Apr", "Mag", "Giu",
            "Lug", "Ago", "Set", "Ott", "Nov", "Dic"
        ]
        totals = monthly_totals_by_year[selected_year]

        fig = go.Figure(data=[
            go.Bar(x=months, y=totals, marker_color="#3f51b5")
        ])
        fig.update_layout(
            title=f"Fatturato Mensile - {selected_year}",
            xaxis_title="Mese",
            yaxis_title="Totale €",
            template="simple_white"
        )

        st.plotly_chart(fig, use_container_width=True)

    if fatture:
        # === RICERCA ===
        search_term = st.text_input("🔍 Cerca per cliente, descrizione o numero fattura").lower()

        # === RAGGRUPPAMENTO ===
        from collections import defaultdict
        archive = defaultdict(lambda: defaultdict(list))
        annual_stats = defaultdict(lambda: {"totale": 0.0, "count": 0})

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

            if search_term:
                match = (
                        search_term in str(fattura['numero_fattura']).lower()
                        or search_term in fattura['cliente'].lower()
                        or search_term in fattura['descrizione'].lower()
                )
                if not match:
                    continue

            date = datetime.datetime.strptime(fattura['data'], "%Y-%m-%d")
            year = str(date.year)
            month = date.strftime("%B")

            archive[year][month].append(fattura)
            annual_stats[year]["totale"] += fattura["totale"]
            annual_stats[year]["count"] += 1

        # === STATS ANNUALI ===
        st.markdown("### 📊 Statistiche Annuali")
        for year in sorted(annual_stats.keys(), reverse=True):
            total = annual_stats[year]["totale"]
            count = annual_stats[year]["count"]
            st.markdown(f"**{year}** — 💰 Totale: €{total:.2f} | 🧾 Fatture: {count}")

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
                from utils.email_utils import send_invoice_email
                if st.button(f"📧 Cliente", key=f"email_{f[0]}"):
                    subject = f"Fattura n. {fattura['numero_fattura']}"
                    body = f"Ciao {fattura['cliente']},\n\nIn allegato trovi la tua fattura.\nGrazie!"
                    success = send_invoice_email(fattura['email'], subject, body, pdf_path)
                    if success:
                        st.success("✅ Email inviata!")
                    else:
                        st.error("❌ Errore nell'invio.")

            with col3:
                if st.button(f"📤 PA", key=f"sdi_{f[0]}"):
                    xml_path = generate_fattura_xml(fattura)
                    subject = f"Fattura Elettronica n. {fattura['numero_fattura']}"
                    body = "In allegato la fattura XML conforme a FatturaPA."
                    success = send_via_pec("sdi01@pec.fatturapa.it", subject, body, xml_path)
                    if success:
                        st.success("✅ Inviata via PEC!")
                    else:
                        st.error("❌ Invio a SDI fallito.")

            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("🔍 Nessuna fattura salvata.")

