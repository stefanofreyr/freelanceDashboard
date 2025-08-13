import os
import streamlit as st
from xml.etree.ElementTree import Element, SubElement, ElementTree
from utils import db

def _get_emitter_data():
    """Recupera dati fiscali mittente da impostazioni utente o segreti."""
    user = st.session_state.get("user") or {}
    settings = db.get_settings(user.get("email")) or {}
    rag_soc = settings.get("ragione_sociale") or user.get("name") or user.get("email")
    indir = settings.get("indirizzo") or ""
    try:
        piva = settings.get("piva") or (
            st.secrets.get("PIVA_EMITTENTE") if hasattr(st, "secrets") else None) or "IT01234567890"
    except Exception:
        piva = settings.get("piva") or "IT01234567890"
    return rag_soc, indir, piva

def generate_fattura_xml(fattura: dict) -> str:
    numero = str(fattura["numero_fattura"])
    rag_soc, indir, piva = _get_emitter_data()

    # Recupero sicuro di user e settings
    user = (st.session_state.get("user") or {})
    settings = db.get_settings(user.get("email")) or {}

    # IVA di default: priorità a quella della fattura (se presente), altrimenti settings, altrimenti 22.0
    def _to_float(x, fallback=None):
        try:
            return float(x)
        except Exception:
            return fallback

    iva_default = _to_float(fattura.get("iva"), None)
    if iva_default is None:
        iva_default = _to_float(settings.get("iva_default"), 22.0)

    os.makedirs("invoices_xml", exist_ok=True)
    filename = f"{piva}_Fattura_{numero}.xml"
    path = os.path.join("invoices_xml", filename)

    # === ELEMENTI PRINCIPALI ===
    FatturaElettronica = Element("p:FatturaElettronica", {
        "xmlns:ds": "http://www.w3.org/2000/09/xmldsig#",
        "xmlns:p": "http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2",
        "versione": "FPR12"
    })

    header = SubElement(FatturaElettronica, "FatturaElettronicaHeader")

    # DatiTrasmissione
    trasmissione = SubElement(header, "DatiTrasmissione")
    id_trasmittente = SubElement(trasmissione, "IdTrasmittente")
    SubElement(id_trasmittente, "IdPaese").text = "IT"
    SubElement(id_trasmittente, "IdCodice").text = piva.replace("IT", "")
    SubElement(trasmissione, "ProgressivoInvio").text = numero.zfill(5)
    SubElement(trasmissione, "FormatoTrasmissione").text = "FPR12"
    SubElement(trasmissione, "CodiceDestinatario").text = "0000000"

    # CedentePrestatore
    cedente = SubElement(header, "CedentePrestatore")
    dati_anagrafici = SubElement(cedente, "DatiAnagrafici")
    id_fiscale = SubElement(dati_anagrafici, "IdFiscaleIVA")
    SubElement(id_fiscale, "IdPaese").text = "IT"
    SubElement(id_fiscale, "IdCodice").text = piva.replace("IT", "")
    SubElement(dati_anagrafici, "CodiceFiscale").text = piva.replace("IT", "")
    anagrafica = SubElement(dati_anagrafici, "Anagrafica")
    SubElement(anagrafica, "Denominazione").text = rag_soc
    SubElement(dati_anagrafici, "RegimeFiscale").text = "RF19"

    sede = SubElement(cedente, "Sede")
    SubElement(sede, "Indirizzo").text = indir or "Indirizzo non specificato"
    SubElement(sede, "CAP").text = "00000"
    SubElement(sede, "Comune").text = "Comune"
    SubElement(sede, "Provincia").text = "PR"
    SubElement(sede, "Nazione").text = "IT"

    # CessionarioCommittente
    cessionario = SubElement(header, "CessionarioCommittente")
    ana_cli = SubElement(cessionario, "DatiAnagrafici")
    anagrafica_cliente = SubElement(ana_cli, "Anagrafica")
    SubElement(anagrafica_cliente, "Denominazione").text = fattura["cliente"]
    sede_cli = SubElement(cessionario, "Sede")
    SubElement(sede_cli, "Indirizzo").text = "Indirizzo cliente"
    SubElement(sede_cli, "CAP").text = "00000"
    SubElement(sede_cli, "Comune").text = "Comune"
    SubElement(sede_cli, "Provincia").text = "PR"
    SubElement(sede_cli, "Nazione").text = "IT"

    # Body
    body = SubElement(FatturaElettronica, "FatturaElettronicaBody")
    dati_generali = SubElement(body, "DatiGenerali")
    doc = SubElement(dati_generali, "DatiGeneraliDocumento")
    SubElement(doc, "TipoDocumento").text = "TD01"
    SubElement(doc, "Divisa").text = "EUR"
    SubElement(doc, "Data").text = fattura["data"]
    SubElement(doc, "Numero").text = numero

    dettagli = SubElement(body, "DatiBeniServizi")
    linea = SubElement(dettagli, "DettaglioLinee")
    SubElement(linea, "NumeroLinea").text = "1"
    SubElement(linea, "Descrizione").text = fattura["descrizione"]
    SubElement(linea, "Quantita").text = "1.00"
    SubElement(linea, "PrezzoUnitario").text = f"{fattura['importo']:.2f}"
    SubElement(linea, "PrezzoTotale").text = f"{fattura['totale']:.2f}"
    SubElement(linea, "AliquotaIVA").text = f"{fattura.get('iva') or iva_default:.2f}"

    riepilogo = SubElement(dettagli, "DatiRiepilogo")
    SubElement(riepilogo, "AliquotaIVA").text = f"{fattura.get('iva') or iva_default:.2f}"
    SubElement(riepilogo, "ImponibileImporto").text = f"{fattura['importo']:.2f}"
    SubElement(riepilogo, "Imposta").text = f"{fattura['totale'] - fattura['importo']:.2f}"
    SubElement(riepilogo, "EsigibilitaIVA").text = "I"

    tree = ElementTree(FatturaElettronica)
    tree.write(path, encoding="utf-8", xml_declaration=True)

    return path
