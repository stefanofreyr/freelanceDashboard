# modules/landing.py
import streamlit as st

# --- STYLES (una volta sola) ---
def inject_styles():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;500;700&display=swap');

        /* Applica il font a tutta l'app */
        .stApp, .stApp * {
            font-family: 'Manrope', sans-serif !important;
        }

        body {
            background-color: #f9f9fb;
        }

        /* HERO: tutto in un solo blocco, niente div aperti/chiusi su chiamate diverse */
        .hero {
            background: linear-gradient(0deg, rgba(0,0,0,0.35), rgba(0,0,0,0.35)),
                        url('https://i.postimg.cc/7YMNrBRP/logo.png') center/cover no-repeat;
            min-height: 78vh;
            color: #fff;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            border-radius: 12px;
            padding: 2.5rem 1.5rem;
        }
        .hero h1 { font-size: clamp(2rem, 4vw, 3rem); margin: 0 0 .5rem 0; }
        .hero p  { font-size: clamp(1rem, 2.2vw, 1.25rem); opacity: .95; margin: 0; }
        .cta {
            display: inline-block;
            margin-top: 1.25rem;
            padding: .75rem 1.25rem;
            background: #e94560;
            color: #fff !important;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 700;
        }

        .section-title { color: #1f4068; font-size: 2rem; margin: 2rem 0 1rem; }
        .card { background: #fff; padding: 1.25rem; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.06); }
        .muted { color: #667085; }

        /* anchor spacing per simulare navbar alta */
        .anchor { position: relative; top: -80px; visibility: hidden; height: 0; }
    </style>
    """, unsafe_allow_html=True)

# --- SEZIONI ---
def show_hero():
    hero_html = """
    <section class="hero">
        <h1>SicilX Innovations</h1>
        <p>La piattaforma per liberi professionisti</p>
        <a class="cta" href="#login">Inizia Subito</a>
    </section>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

def show_services():
    st.markdown('<span id="servizi" class="anchor"></span>', unsafe_allow_html=True)
    st.markdown("## 🔧 Servizi Offerti")
    st.write(
        "- 📄 Creazione e invio fatture (PDF & PEC)\n"
        "- 📨 Integrazione SDI & Agenzia delle Entrate\n"
        "- 📅 Calendario e promemoria visite guidate\n"
        "- 🤖 Automazioni smart per risparmiare tempo"
    )

def show_pricing():
    st.markdown('<span id="pricing" class="anchor"></span>', unsafe_allow_html=True)
    st.markdown("## 💰 Prezzi")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### Free")
        st.markdown("- ✔️ 3 fatture/mese\n- ❌ PEC/SDI\n\n**€0/mese**")
        st.button("Prova Free", key="p_free")
    with c2:
        st.markdown("#### Pro")
        st.markdown("- ✔️ Illimitato\n- ✔️ PEC + SDI\n\n**€14/mese**")
        st.button("Attiva Pro", key="p_pro")
    with c3:
        st.markdown("#### Premium")
        st.markdown("- ✔️ Tutto incluso\n- ✔️ PEC dedicata\n\n**€29/mese**")
        st.button("Attiva Premium", key="p_premium")

def show_login():
    st.markdown('<span id="login" class="anchor"></span>', unsafe_allow_html=True)
    st.markdown("## 🔐 Login / Registrazione")
    with st.form("login_form"):
        st.text_input("Email", key="login_email")
        st.text_input("Password", type="password", key="login_pwd")
        if st.form_submit_button("Accedi / Registrati"):
            st.success("Funzionalità in arrivo…")

def show_contacts():
    st.markdown('<span id="contatti" class="anchor"></span>', unsafe_allow_html=True)
    st.markdown("## 📬 Contattaci")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Nome", key="contact_name")
        st.text_input("Email", key="contact_email")
    with c2:
        st.text_area("Messaggio", key="contact_msg")
        if st.button("Invia Messaggio", key="send_msg"):
            st.success("Grazie per averci contattato, ti risponderemo presto.")

def show_footer():
    st.markdown("---")
    st.markdown("<center class='muted'>© 2025 Silican Innovations – Made in Sicilia 🇮🇹</center>", unsafe_allow_html=True)

# --- ENTRYPOINT DELLA PAGINA ---
def show():
    inject_styles()
    show_hero()
    show_services()
    show_pricing()
    show_login()
    show_contacts()
    show_footer()
