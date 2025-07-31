from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet
import os

def generate_invoice_pdf(fattura):
    numero_fattura = fattura["numero_fattura"]
    cliente = fattura["cliente"]
    descrizione = fattura["descrizione"]
    importo = fattura["importo"]
    iva = fattura["iva"]
    totale = fattura["totale"]
    data = fattura["data"]
    email = fattura["email"]

    file_name = f"fattura_{numero_fattura.replace('/', '_')}.pdf"
    file_path = os.path.join("data", "pdf", file_name)
    os.makedirs("data/pdf", exist_ok=True)

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Logo
    logo_path = "assets/logo.png"
    if os.path.exists(logo_path):
        img = Image(logo_path, width=100, height=50)
        elements.append(img)
        elements.append(Spacer(1, 12))

    # Intestazione fiscale (mittente)
    intestazione = [
        "Silican Innovations",
        "Via dell'Etna 42, 95100 Catania (CT)",
        "P.IVA: 12345678901",
        "Email: info@silican.it",
        "Tel: +39 095 1234567"
    ]
    for riga in intestazione:
        elements.append(Paragraph(riga, styles['Normal']))
    elements.append(Spacer(1, 20))

    # Titolo fattura
    elements.append(Paragraph(f"<b>Fattura n. {numero_fattura}</b>", styles['Title']))
    elements.append(Paragraph(f"Data: {data}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Dati Cliente
    elements.append(Paragraph(f"<b>Cliente:</b> {cliente}", styles['Normal']))
    elements.append(Paragraph(f"<b>Email:</b> {email}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Tabella riepilogo
    table_data = [
        ['Descrizione', 'Importo (€)', 'IVA (%)', 'Totale (€)'],
        [descrizione, f"{importo:.2f}", f"{iva:.0f}%", f"{totale:.2f}"]
    ]
    table = Table(table_data, colWidths=[240, 80, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # Clausola finale
    clausola = Paragraph(
        "<i>Pagamento da effettuare entro 30 giorni dalla data della fattura. "
        "Grazie per aver scelto i nostri servizi.</i>",
        styles['Normal']
    )
    elements.append(clausola)

    doc.build(elements)
    return file_path
