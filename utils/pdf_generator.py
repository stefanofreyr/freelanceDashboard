from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
import os

def generate_invoice_pdf(fattura, output_folder="data/pdf"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    file_path = os.path.join(output_folder, f"fattura_{fattura['id']}.pdf")

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Titolo
    title = Paragraph(f"<b>FATTURA #{fattura['id']}</b>", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 1*cm))

    # Info cliente & data
    elements.append(Paragraph(f"<b>Cliente:</b> {fattura['cliente']}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Data:</b> {fattura['data']}", styles["Normal"]))
    elements.append(Spacer(1, 0.5*cm))

    # Tabella dettagli fattura
    data = [
        ["Descrizione", "Importo (€)", "IVA (%)", "Totale (€)"],
        [fattura['descrizione'], f"{fattura['importo']:.2f}", f"{fattura['iva']}%", f"{fattura['totale']:.2f}"]
    ]

    table = Table(data, colWidths=[8*cm, 3*cm, 3*cm, 3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('TOPPADDING', (0,0), (-1,0), 6),
    ]))
    elements.append(table)

    # Firma finale
    elements.append(Spacer(1, 2*cm))
    elements.append(Paragraph("Grazie per aver scelto i nostri servizi!", styles["Italic"]))

    doc.build(elements)

    return file_path
