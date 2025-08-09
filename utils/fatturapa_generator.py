import os
import streamlit as st
import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree

def _get_emitter_piva() -> str:
    """
    P.IVA emittente:
    1) .streamlit/secrets.toml -> PIVA_EMITTENTE
    2) env var PIVA_EMITTENTE
    3) fallback "IT01234567890"
    """
    return st.secrets.get("PIVA_EMITTENTE", os.environ.get("PIVA_EMITTENTE", "IT01234567890"))


def generate_fattura_xml(fattura: dict) -> str:
    """
    Crea l'XML FatturaPA e lo salva in invoices_xml/.
    Si aspetta che 'fattura' contenga almeno: numero_fattura, data, cliente, totale, ecc.
    """
    numero = str(fattura["numero_fattura"])
    piva = _get_emitter_piva()

    # Assicurati che la cartella esista
    os.makedirs("invoices_xml", exist_ok=True)

    # Nome file con P.IVA emittente
    filename = f"{piva}_Fattura_{numero}.xml"
    xml_path = os.path.join("invoices_xml", filename)
    nome_file = f"{piva}_Fattura_{numero}.xml" # Sostituisci con la tua P.IVA
    path = os.path.join("invoices_xml", nome_file)

    # === ELEMENTI PRINCIPALI ===
    FatturaElettronica = Element("p:FatturaElettronica", {
        "xmlns:ds": "http://www.w3.org/2000/09/xmldsig#",
        "xmlns:p": "http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2",
        "versione": "FPR12"
    })

    header = SubElement(FatturaElettronica, "FatturaElettronicaHeader")

    # === DatiTrasmissione (obbligatorio prima)
    trasmissione = SubElement(header, "DatiTrasmissione")
    id_trasmittente = SubElement(trasmissione, "IdTrasmittente")
    SubElement(id_trasmittente, "IdPaese").text = "IT"
    SubElement(id_trasmittente, "IdCodice").text = "01234567890"
    SubElement(trasmissione, "ProgressivoInvio").text = numero.zfill(5)
    SubElement(trasmissione, "FormatoTrasmissione").text = "FPR12"
    SubElement(trasmissione, "CodiceDestinatario").text = "0000000"

    # === CedentePrestatore
    cedente = SubElement(header, "CedentePrestatore")
    dati_anagrafici = SubElement(cedente, "DatiAnagrafici")
    id_fiscale = SubElement(dati_anagrafici, "IdFiscaleIVA")
    SubElement(id_fiscale, "IdPaese").text = "IT"
    SubElement(id_fiscale, "IdCodice").text = "01234567890"
    SubElement(dati_anagrafici, "CodiceFiscale").text = "01234567890"
    anagrafica = SubElement(dati_anagrafici, "Anagrafica")
    SubElement(dati_anagrafici, "RegimeFiscale").text = "RF19"
    SubElement(anagrafica, "Denominazione").text = "Silican Innovations"

    sede = SubElement(cedente, "Sede")
    SubElement(sede, "Indirizzo").text = "Via Esempio 123"
    SubElement(sede, "CAP").text = "90100"
    SubElement(sede, "Comune").text = "Palermo"
    SubElement(sede, "Provincia").text = "PA"
    SubElement(sede, "Nazione").text = "IT"

    # === CessionarioCommittente
    cessionario = SubElement(header, "CessionarioCommittente")
    ana_cli = SubElement(cessionario, "DatiAnagrafici")
    SubElement(ana_cli, "CodiceFiscale").text = "RSSMRA85M01H501Z"  # esempio
    #SubElement(ana_cli, "RegimeFiscale").text = "RF19"  # anche se non richiesto, alcuni XSD lo vogliono
    anagrafica_cliente = SubElement(ana_cli, "Anagrafica")
    SubElement(anagrafica_cliente, "Denominazione").text = fattura["cliente"]
    sede_cli = SubElement(cessionario, "Sede")
    SubElement(sede_cli, "Indirizzo").text = "Via Cliente 1"
    SubElement(sede_cli, "CAP").text = "90100"
    SubElement(sede_cli, "Comune").text = "Palermo"
    SubElement(sede_cli, "Provincia").text = "PA"
    SubElement(sede_cli, "Nazione").text = "IT"

    # === BODY
    body = SubElement(FatturaElettronica, "FatturaElettronicaBody")
    dati_generali = SubElement(body, "DatiGenerali")
    doc = SubElement(dati_generali, "DatiGeneraliDocumento")
    SubElement(doc, "TipoDocumento").text = "TD01"
    SubElement(doc, "Divisa").text = "EUR"
    SubElement(doc, "Data").text = fattura["data"]
    SubElement(doc, "Numero").text = numero

    # Dettaglio linee
    dettagli = SubElement(body, "DatiBeniServizi")
    linea = SubElement(dettagli, "DettaglioLinee")
    SubElement(linea, "NumeroLinea").text = "1"
    SubElement(linea, "Descrizione").text = fattura["descrizione"]
    SubElement(linea, "Quantita").text = "1.00"
    SubElement(linea, "PrezzoUnitario").text = f"{fattura['importo']:.2f}"
    SubElement(linea, "PrezzoTotale").text = f"{fattura['totale']:.2f}"
    SubElement(linea, "AliquotaIVA").text = f"{fattura['iva']:.2f}"

    # Riepilogo IVA
    riepilogo = SubElement(dettagli, "DatiRiepilogo")
    SubElement(riepilogo, "AliquotaIVA").text = f"{fattura['iva']:.2f}"
    SubElement(riepilogo, "ImponibileImporto").text = f"{fattura['importo']:.2f}"
    SubElement(riepilogo, "Imposta").text = f"{fattura['totale'] - fattura['importo']:.2f}"
    SubElement(riepilogo, "EsigibilitaIVA").text = "I"

    tree = ElementTree(FatturaElettronica)
    tree.write(path, encoding="utf-8", xml_declaration=True)

    from utils.validator import validate_with_imports

    # Percorsi degli XSD
    main_xsd = "utils/schemas/Schema_VFPA12_V1.2.3.xsd"
    xmldsig_xsd = "utils/schemas/xmldsig-core-schema.xsd"

    # Validazione
    success, msg = validate_with_imports(path, main_xsd, xmldsig_xsd)
    print(msg)

    return path



