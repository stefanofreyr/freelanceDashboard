from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
import os

def generate_test_pdf(output_folder="data/pdf"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    file_path = os.path.join(output_folder, "test_fattura.pdf")

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Titolo
    title = Paragraph("<b>FATTURA #TEST01</b>", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 1*cm))

    # Info cliente & data
    elements.append(Paragraph("<b>Cliente:</b> Mario Rossi", styles["Normal"]))
    elements.append(Paragraph("<b>Data:</b> 2025-07-30", styles["Normal"]))
    elements.append(Spacer(1, 0.5*cm))

    # Tabella dettagli fattura
    data = [
        ["Descrizione", "Importo (€)", "IVA (%)", "Totale (€)"],
        ["Tour dell'Etna e Taormina", "120.00", "22%", "146.40"]
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
    print(f"PDF generato: {file_path}")

if __name__ == "__main__":
    generate_test_pdf()
