import os
import json
import datetime
import streamlit as st
from utils import db
from utils.logging_setup import get_app_logger

# === Helpers ===

def _has_openai():
    try:
        import openai  # noqa
        # Serve anche la key
        return bool(getattr(st, "secrets", {}).get("OPENAI_API_KEY"))
    except Exception:
        return False


def _ai_generate(prompt: str, temperature: float = 0.2, max_tokens: int = 600) -> str:
    """
    Prova OpenAI → se fallisce per quota o assenza key, prova Groq → altrimenti fallback locale.
    """
    import os
    import streamlit as st

    def _fallback(text: str) -> str:
        lines = [l.strip() for l in (text or "").splitlines() if l.strip()]
        if not lines:
            return "Nessun contenuto sufficiente per generare un risultato."
        return (
            "Bozza generata (fallback locale):\n\n"
            "Oggetto: Proposta di preventivo\n\n"
            "Gentile Cliente,\n\n"
            + "\n".join(f"- {l}" for l in lines[:12]) +
            "\n\nResto a disposizione per eventuali chiarimenti.\n\nCordiali saluti,\nIl tuo nome"
        )

    # ---- 1) Tentativo con OpenAI ----
    try:
        from openai import OpenAI
        openai_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if openai_key:
            client = OpenAI(api_key=openai_key)
            resp = client.chat.completions.create(
                model=st.secrets.get("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "Sei un assistente per freelance italiani. Scrivi email pronte da inviare, chiare e sintetiche."},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return (resp.choices[0].message.content or "").strip()
    except Exception as ex:
        if "insufficient_quota" in str(ex) or "RateLimitError" in str(ex):
            st.warning("Quota OpenAI esaurita, passo a Groq gratuito...")
        else:
            st.info(f"OpenAI non disponibile: {ex}")

    # ---- 2) Tentativo con Groq ----
    try:
        import requests
        groq_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
        if groq_key:
            def groq_call(model_name):
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
                payload = {
                    "model": model_name,
                    "messages": [
                        {"role": "system",
                         "content": "Sei un assistente per freelance italiani. Scrivi email pronte da inviare, chiare e sintetiche."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
                r = requests.post(url, headers=headers, json=payload, timeout=30)
                r.raise_for_status()
                return r.json()["choices"][0]["message"]["content"].strip()

            # Primo tentativo: modello grande
            try:
                return groq_call("llama3-70b-8192")
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 503:
                    st.warning("Groq 70B non disponibile, passo a 8B...")
                    return groq_call("llama3-8b-8192")
                else:
                    raise
    except Exception as ex:
        st.info(f"Groq non disponibile: {ex}")

    # ---- 3) Fallback locale ----
    return _fallback(prompt)



def _save_text(doc_text: str, filename_prefix: str, user_email: str) -> str:
    base = os.path.join("documents", user_email)
    os.makedirs(base, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(base, f"{filename_prefix}_{ts}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc_text)
    return path

def _client_names(user_email: str, user_id: int):
    try:
        rows = db.lista_clienti_by_user_id(user_id) or []
        names = sorted({(r.get("nome") or "").strip() for r in rows if r.get("nome")})
        return [n for n in names if n]
    except Exception:
        return []

# === UI ===

def show():
    st.title("⚙️ Automazioni & AI (demo)")

    logger = get_app_logger()
    user = st.session_state.get("user") or {}
    user_email = user.get("email")
    user_id = user.get("id")

    if not user_email or not user_id:
        st.error("Devi effettuare il login.")
        st.stop()

    st.info(
        "Questa sezione mostra esempi pratici di **AI generativa** nel workflow: preventivi, riassunti, "
        "testi fattura, follow‑up, cold outreach. Funziona anche **senza API key** (fallback locale). "
        "Per usare un modello AI, aggiungi `OPENAI_API_KEY` nei Secrets."
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "✉️ Preventivo email",
        "🗒️ To‑do da note cliente",
        "🧾 Descrizione fattura",
        "🔁 Follow‑up post consegna",
        "📣 Cold outreach"
    ])

    # ---- 1) Preventivo email -------------------------------------------------
    with tab1:
        st.subheader("✉️ Stesura email di preventivo")

        clienti = _client_names(user_email, user_id)
        col_a, col_b = st.columns(2)
        with col_a:
            cliente = st.selectbox("Cliente", ["(generico)"] + clienti)
        with col_b:
            tono = st.selectbox("Tono", ["professionale", "amichevole", "tecnico", "formale"], index=0)

        contesto = st.text_area(
            "Dettagli lavoro (bullet points)",
            placeholder="- Sviluppo landing\n- Integrazione pagamento Stripe\n- Consegna 2 settimane",
            height=120
        )
        prezzo = st.text_input("Range/prezzo (opzionale)", placeholder="Es. 1200–1500€ o 75€/h")

        prompt = f"""Scrivi una email sintetica di preventivo in italiano.
Destinatario: {cliente}.
Tono: {tono}.
Dettagli:
{contesto}

Se presente, integra prezzo: {prezzo or 'N/D'}.
Chiudi con call-to-action chiara."""
        if st.button("🧠 AI — Genera testo"):
            testo = _ai_generate(prompt, temperature=0.4)
            st.text_area("Anteprima", value=testo, height=260)
            if st.button("💾 Salva in Documenti", key="save_quote"):
                path = _save_text(testo, "preventivo_email", user_email)
                logger.info("automation_saved category=quote path=%s", path)
                st.success(f"Salvato in: `{path}`")

    # ---- 2) To‑do da note cliente -------------------------------------------
    with tab2:
        st.subheader("🗒️ Estrarre To‑do da note cliente")
        raw_notes = st.text_area("Incolla le note/verbale incontro", height=220)
        priority = st.selectbox("Priorità", ["mista", "alta→bassa", "scadenza"], index=0)

        prompt = f"""Dalle seguenti note del cliente, estrai una lista di TODO con:
- titolo breve
- descrizione essenziale
- priorità (Alta/Media/Bassa)
- stima ore

Riporta in formato elenco markdown con checkbox.

Note:
{raw_notes}

Ordina per: {priority}."""
        if st.button("🧠 AI — Genera To‑do"):
            testo = _ai_generate(prompt, temperature=0.2)
            st.text_area("Lista To‑do (Markdown)", value=testo, height=280)
            if st.button("💾 Salva in Documenti", key="save_todos"):
                path = _save_text(testo, "todo_from_notes", user_email)
                logger.info("automation_saved category=todos path=%s", path)
                st.success(f"Salvato in: `{path}`")

    # ---- 3) Descrizione fattura ---------------------------------------------
    with tab3:
        st.subheader("🧾 Generare descrizione fattura da attività")
        attività = st.text_area(
            "Attività svolte (una per riga)",
            placeholder="- Setup repository e CI\n- Refactor moduli fatture\n- Test end‑to‑end\n- Call con stakeholder",
            height=160
        )
        col1, col2 = st.columns(2)
        with col1:
            mese_ref = st.selectbox("Periodo", ["mese corrente", "mese precedente", "personalizzato"], index=0)
        with col2:
            ansa = st.text_input("Riferimenti ordine/progetto (opz.)", placeholder="PO #1234 / Sprint 8")

        if mese_ref == "personalizzato":
            periodo = st.text_input("Indica il periodo (es. 1–15 Agosto 2025)")
        else:
            today = datetime.date.today()
            if mese_ref == "mese corrente":
                periodo = today.strftime("%B %Y")
            else:
                prev = (today.replace(day=1) - datetime.timedelta(days=1))
                periodo = prev.strftime("%B %Y")

        stile = st.selectbox("Stile descrizione", ["tecnico", "contrattuale", "sintetico"], index=2)

        prompt = f"""Sintetizza le attività di seguito in una **descrizione fattura** (una riga o due), tono {stile}.
Periodo: {periodo}. Riferimenti: {ansa or 'N/D'}.
Attività:
{attività}"""
        if st.button("🧠 AI — Genera descrizione"):
            testo = _ai_generate(prompt, temperature=0.3, max_tokens=200)
            st.text_area("Descrizione proposta", value=testo, height=140)
            if st.button("💾 Salva in Documenti", key="save_desc"):
                path = _save_text(testo, "descrizione_fattura", user_email)
                logger.info("automation_saved category=invoice_desc path=%s", path)
                st.success(f"Salvato in: `{path}`")

    # ---- 4) Follow‑up post consegna -----------------------------------------
    with tab4:
        st.subheader("🔁 Follow‑up dopo consegna")
        consegna = st.text_area("Cosa hai consegnato?", placeholder="Release v1.2 e documento di handover", height=110)
        outcome = st.selectbox("Esito progetto", ["positivo", "neutro", "con criticità"], index=0)
        upsell = st.checkbox("Proponi step successivi/upsell", value=True)

        prompt = f"""Scrivi un breve follow‑up post consegna in italiano.
Esito: {outcome}.
Contenuti consegnati: {consegna}.
Includi (se spuntato) proposta di step successivi: {upsell}.
Chiudi con richiesta di feedback e disponibilità per chiarimenti."""
        if st.button("🧠 AI — Genera follow‑up"):
            testo = _ai_generate(prompt, temperature=0.4, max_tokens=280)
            st.text_area("Email follow‑up", value=testo, height=220)
            if st.button("💾 Salva in Documenti", key="save_followup"):
                path = _save_text(testo, "followup_post_consegna", user_email)
                logger.info("automation_saved category=followup path=%s", path)
                st.success(f"Salvato in: `{path}`")

    # ---- 5) Cold outreach ----------------------------------------------------
    with tab5:
        st.subheader("📣 Cold outreach personalizzato")
        settore = st.text_input("Settore cliente", placeholder="es. e‑commerce moda")
        problema = st.text_area("Dolore/necessità tipica", placeholder="Checkout lento, tasso abbandono alto", height=110)
        valore = st.text_area("Valore che offri", placeholder="Ottimizzazione performance, A/B testing, refactor checkout", height=110)
        prova = st.text_input("Prova sociale (opz.)", placeholder="Case study, referenza, cifra d'impatto…")

        prompt = f"""Scrivi una breve email di cold outreach in italiano, personalizzata.
Settore: {settore}
Dolore tipico: {problema}
Valore offerto: {valore}
Prova sociale: {prova or 'N/D'}
Tono: professionale e concreto, massimo 120 parole, CTA chiara e leggera."""
        if st.button("🧠 AI — Genera outreach"):
            testo = _ai_generate(prompt, temperature=0.5, max_tokens=220)
            st.text_area("Bozza outreach", value=testo, height=220)
            if st.button("💾 Salva in Documenti", key="save_outreach"):
                path = _save_text(testo, "cold_outreach", user_email)
                logger.info("automation_saved category=outreach path=%s", path)
                st.success(f"Salvato in: `{path}`")

    # Footer info
    st.caption("Suggerimento: personalizza i prompt e salva le bozze in Documenti; puoi riutilizzarle e adattarle al volo.")
