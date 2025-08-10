import os, zipfile, io, datetime

def build_backup_zip_for_user(email: str):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        # DB (intero: semplice per MVP)
        if os.path.exists("data/fatture.db"):
            z.write("data/fatture.db", "data/fatture.db")

        # Documenti dell'utente
        base = os.path.join("documents", email)
        if os.path.exists(base):
            for root, _, files in os.walk(base):
                for f in files:
                    p = os.path.join(root, f)
                    z.write(p, os.path.relpath(p, "."))

        # XML fatture
        if os.path.exists("invoices_xml"):
            for f in os.listdir("invoices_xml"):
                path = os.path.join("invoices_xml", f)
                if os.path.isfile(path):
                    z.write(path, f"invoices_xml/{f}")

        # Log (opzionale)
        if os.path.exists("logs"):
            for f in os.listdir("logs"):
                p = os.path.join("logs", f)
                if os.path.isfile(p):
                    z.write(p, f"logs/{f}")

    buf.seek(0)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return buf, f"FAi_backup_{ts}.zip"
