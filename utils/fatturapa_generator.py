import os
import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree

def generate_fattura_xml(fattura: dict):
    """
    Genera un file XML in formato FatturaPA a partire dai dati fattura forniti
    """
    numero = str(fattura["numero_fattura"])
    nome_file = f"IT01234567890_Fattura_{numero}.xml"  # Sostituisci con la tua P.IVA
    path = os.path.join("invoices_xml", nome_file)

    # === ELEMENTI PRINCIPALI ===
    FatturaElettronica = Element("p:FatturaElettronica", {
        "xmlns:ds": "http://www.w3.org/2000/09/xmldsig#",
        "xmlns:p": "http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2",
        "versione": "FPR12"
    })

    # === HEADER ===
    header = SubElement(FatturaElettronica, "FatturaElettronicaHeader")
    cedente = SubElement(header, "CedentePrestatore")
    dati_anagrafici = SubElement(cedente, "DatiAnagrafici")
    SubElement(dati_anagrafici, "IdFiscaleIVA").text = "IT01234567890"
    SubElement(dati_anagrafici, "CodiceFiscale").text = "01234567890"
    SubElement(dati_anagrafici, "Anagrafica").text = "Silican Innovations"

    cessionario = SubElement(header, "CessionarioCommittente")
    anagrafica_cliente = SubElement(cessionario, "Anagrafica")
    SubElement(anagrafica_cliente, "Denominazione").text = fattura["cliente"]

    # === BODY ===
    body = SubElement(FatturaElettronica, "FatturaElettronicaBody")
    datiGenerali = SubElement(body, "DatiGenerali")
    datiGeneraliDocumento = SubElement(datiGenerali, "DatiGeneraliDocumento")
    SubElement(datiGeneraliDocumento, "TipoDocumento").text = "TD01"
    SubElement(datiGeneraliDocumento, "Divisa").text = "EUR"
    SubElement(datiGeneraliDocumento, "Data").text = fattura["data"]
    SubElement(datiGeneraliDocumento, "Numero").text = numero

    # === DETTAGLI LINEA ===
    dettaglioLinee = SubElement(body, "DatiBeniServizi")
    linea = SubElement(dettaglioLinee, "DettaglioLinee")
    SubElement(linea, "Descrizione").text = fattura["descrizione"]
    SubElement(linea, "Quantita").text = "1.00"
    SubElement(linea, "PrezzoUnitario").text = str(fattura["importo"])
    SubElement(linea, "AliquotaIVA").text = str(fattura["iva"])
    SubElement(linea, "PrezzoTotale").text = str(fattura["totale"])

    # === SALVA XML ===
    tree = ElementTree(FatturaElettronica)
    tree.write(path, encoding="utf-8", xml_declaration=True)
    return path
