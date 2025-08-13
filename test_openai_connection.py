import os

try:
    from openai import OpenAI
except ImportError:
    raise RuntimeError("Libreria openai non installata. Esegui: pip install --upgrade openai")

# 1️⃣ Legge la chiave da variabile ambiente
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY non trovata nelle variabili d'ambiente.\n"
        "Se lavori in locale, puoi fare:\n"
        "   setx OPENAI_API_KEY \"sk-...\"   (Windows)\n"
        "   export OPENAI_API_KEY=\"sk-...\" (Mac/Linux)\n"
    )

# 2️⃣ Inizializza il client
client = OpenAI(api_key=api_key)

# 3️⃣ Prompt di test
prompt = """
Scrivi una breve email professionale di preventivo per un servizio di sviluppo web.
Prezzo: 500€, destinatario: Mario Rossi, tono: formale.
"""

print("Chiamata API in corso...\n")

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Sei un assistente che scrive email professionali in italiano."},
        {"role": "user", "content": prompt},
    ],
    temperature=0.3,
    max_tokens=300,
)

email_testo = resp.choices[0].message.content
print("=== EMAIL GENERATA ===\n")
print(email_testo)
