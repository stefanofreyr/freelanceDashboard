import streamlit as st
from utils import db
import datetime as _dt
import os

def show():
    if "user" not in st.session_state:
        st.error("⚠️ Devi effettuare il login per accedere alla dashboard.")
        return

    user = st.session_state["user"]
    user_id = user["id"]
    nome = user.get("name") or user.get("email")

    st.title(f"📊 Benvenuto/a, {nome}")
    st.caption("Ecco un riepilogo della tua attività recente")

    # === FATTURE ===
    fatture = db.get_all_invoices_by_user_id(user_id)

    # helper per compatibilità (dict o tuple)
    def _get(row, key, idx=None):
        if isinstance(row, dict):
            return row.get(key)
        return row[idx] if idx is not None else None

    def _parse_date(s):
        try:
            return _dt.date.fromisoformat(str(s))
        except Exception:
            return None

    today = _dt.date.today()
    this_year = today.year
    this_month = today.month

    totale_fatture = len(fatture)
    totale_importi = 0.0
    month_importi = 0.0
    year_importi = 0.0

    for f in fatture:
        d = _parse_date(_get(f, "data", 5))
        tot = float(_get(f, "totale", 7) or 0)
        totale_importi += tot
        if d:
            if d.year == this_year:
                year_importi += tot
                if d.month == this_month:
                    month_importi += tot

    ticket_medio = (totale_importi / totale_fatture) if totale_fatture else 0.0

    # KPI layout
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📄 Fatture Totali", totale_fatture)
    c2.metric("💰 Totale Fatturato", f"€ {totale_importi:.2f}")
    c3.metric(f"🗓️ Mese {this_month:02d}", f"€ {month_importi:.2f}")
    c4.metric(f"📆 {this_year}", f"€ {year_importi:.2f}")
    st.caption(f"🎟️ Ticket medio fattura: **€ {ticket_medio:.2f}**")

    # === EVENTI ===
    eventi = db.lista_eventi_futuri_by_user_id(user_id)
    eventi_prossimi = [
        e for e in eventi
        if _dt.date.fromisoformat(e["data"]) <= _dt.date.today() + _dt.timedelta(days=7)
    ]

    st.markdown("### 📅 Eventi dei prossimi 7 giorni")
    if eventi_prossimi:
        for e in eventi_prossimi:
            st.markdown(f"- **{e['data']} {e['ora']}** — {e['titolo']}")
    else:
        st.info("Nessun evento in arrivo entro la settimana.")

    # === LOG PEC ===
    st.markdown("### 📬 Ultimi invii PEC")
    log_path = "logs/pec_log.txt"
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            log_lines = f.readlines()
        log_utente = [line for line in log_lines if f"utente: {user['email']}" in line]
        if log_utente:
            for line in reversed(log_utente[-5:]):
                st.markdown(f"- {line.strip()}")
        else:
            st.info("Nessun invio PEC registrato per questo utente.")
    else:
        st.info("Log PEC non ancora disponibile.")
