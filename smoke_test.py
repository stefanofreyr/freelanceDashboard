#!/usr/bin/env python3
"""
Smoke test for FAi (Freelance Dashboard)

What it does:
1) Ensures required folders exist.
2) Imports core modules (db, fatturapa_generator, validator, pdf_generator).
3) Initializes DB.
4) Generates a sample FatturaPA XML and validates it against XSDs.
5) Generates a sample PDF.
6) Prints a concise PASS/FAIL report.

How to run:
    python smoke_test.py

Run from the project root (the folder that contains app.py and the 'utils' directory).
"""

import os
import sys
import traceback
from datetime import date
from importlib import import_module

RESULTS = []

def ok(msg): RESULTS.append(("PASS", msg))
def ko(msg): RESULTS.append(("FAIL", msg))

def main():
    # 0) project root detection
    root_files = ["app.py", "utils", "modules"]
    if not all(os.path.exists(x) for x in root_files):
        ko("Run this script from the project ROOT (where app.py lives).")
        show()
        sys.exit(1)

    # 1) ensure folders
    for d in ["invoices_xml", "data/pdf", "logs"]:
        try:
            os.makedirs(d, exist_ok=True)
            ok(f"Folder ready: {d}")
        except Exception as e:
            ko(f"Cannot create folder {d}: {e}")

    # 2) imports
    try:
        db = import_module("utils.db")
        ok("Imported utils.db")
    except Exception as e:
        ko(f"Import utils.db failed: {e}")

    try:
        fatt_gen = import_module("utils.fatturapa_generator")
        ok("Imported utils.fatturapa_generator")
    except Exception as e:
        ko(f"Import fatturapa_generator failed: {e}")

    try:
        validator = import_module("utils.validator")
        ok("Imported utils.validator")
    except Exception as e:
        ko(f"Import utils.validator failed: {e}")

    try:
        pdfgen = import_module("utils.pdf_generator")
        ok("Imported utils.pdf_generator")
    except Exception as e:
        ko(f"Import utils.pdf_generator failed: {e}")

    # 3) init DB
    try:
        db.init_db()
        ok("DB initialized (utils.db.init_db)")
    except Exception as e:
        ko(f"DB init failed: {e}")

    # 4) sample invoice XML + validate
    xml_path = None
    try:
        sample = {
            "numero_fattura": 9999,
            "cliente": "Mario Rossi",
            "descrizione": "Servizio di prova",
            "importo": 100.0,
            "iva": 22.0,
            "totale": 122.0,
            "data": str(date.today())
        }
        xml_path = fatt_gen.generate_fattura_xml(sample)
        if not os.path.exists(xml_path):
            raise RuntimeError(f"XML not found at {xml_path}")
        ok(f"XML generated at {xml_path}")
    except Exception as e:
        ko(f"XML generation failed: {e}")

    try:
        if xml_path:
            main_xsd = os.path.join("utils", "schemas", "Schema_VFPA12_V1.2.3.xsd")
            sig_xsd  = os.path.join("utils", "schemas", "xmldsig-core-schema.xsd")
            if not (os.path.exists(main_xsd) and os.path.exists(sig_xsd)):
                raise FileNotFoundError("XSD files missing under utils/schemas")
            success, msg = validator.validate_with_imports(xml_path, main_xsd, sig_xsd)
            if success:
                ok(f"XML validation passed: {msg}")
            else:
                ko(f"XML validation failed: {msg}")
    except Exception as e:
        ko(f"XML validation error: {e}")

    # 5) PDF generation
    try:
        from utils.pdf_generator import generate_invoice_pdf
        pdf_path = generate_invoice_pdf({
            "numero_fattura": 9999,
            "cliente": "Mario Rossi",
            "descrizione": "Servizio di prova",
            "importo": 100.0,
            "iva": 22.0,
            "totale": 122.0,
            "data": str(date.today()),
            "email": "mario.rossi@example.com"
        })
        if not os.path.exists(pdf_path):
            raise RuntimeError(f"PDF not found at {pdf_path}")
        ok(f"PDF generated at {pdf_path}")
    except Exception as e:
        ko(f"PDF generation failed: {e}")

    show()

def show():
    print("\n=== SMOKE TEST REPORT ===")
    passed = sum(1 for s,_ in RESULTS if s=="PASS")
    failed = sum(1 for s,_ in RESULTS if s=="FAIL")
    for status, msg in RESULTS:
        print(f"[{status}] {msg}")
    print(f"\nSummary: {passed} passed, {failed} failed")
    sys.exit(0 if failed==0 else 2)

if __name__ == "__main__":
    main()
