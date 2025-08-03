# TO VALIDATE IF THE INVOICE GENERATED IS COMPLIANT WITH THE SCHEMA

from lxml import etree

class LocalResolver(etree.Resolver):
    def __init__(self, xmldsig_path):
        super().__init__()
        self.xmldsig_path = xmldsig_path

    def resolve(self, url, id, context):
        if url == "xmldsig-core-schema.xsd":
            return self.resolve_filename(self.xmldsig_path, context)
        return None

def validate_with_imports(xml_path, main_xsd_path, xmldsig_xsd_path):
    parser = etree.XMLParser()
    parser.resolvers.add(LocalResolver(xmldsig_xsd_path))

    try:
        with open(main_xsd_path, "rb") as f:
            schema_doc = etree.parse(f, parser)
            schema = etree.XMLSchema(schema_doc)

        with open(xml_path, "rb") as f:
            doc = etree.parse(f, parser)
            schema.assertValid(doc)

        return True, "✅ XML conforme al tracciato FatturaPA"

    except etree.DocumentInvalid as e:
        return False, f"❌ Documento non valido:\n{e}"
    except Exception as e:
        return False, f"⚠️ Errore imprevisto:\n{e}"
