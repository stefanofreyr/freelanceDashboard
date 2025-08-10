# modules/landing.py
import streamlit as st
from utils.auth import auth_block_on_landing

# --- STYLES (una volta sola) ---
def inject_styles():
    st.markdown("""
        <style>
          /* --- Hero --- */
          .hero {
            position: relative;
            min-height: 70vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            color: #fff;
            padding: 4rem 1rem;
            margin: 64px 0 24px;
            border-radius: 16px;
            overflow: hidden;
            background:
              linear-gradient(180deg, rgba(0,0,0,0.45), rgba(0,0,0,0.35)),
              url('https://shorturl.at/z95wq') center/cover no-repeat;
          }
          .hero h1 {
            font-size: clamp(2rem, 5vw, 3.2rem);
            margin: 0 0 0.5rem 0;
            letter-spacing: 0.5px;
          }
          .hero p {
            font-size: clamp(1rem, 2.5vw, 1.25rem);
            opacity: 0.95;
            margin-bottom: 1.25rem;
          }
          .hero .cta {
            display: inline-block;
            margin-top: 0.75rem;
            padding: 0.8rem 1.4rem;
            background: #e94560;
            color: #fff !important;
            border-radius: 10px;
            text-decoration: none;
            font-weight: 700;
            transition: transform .15s ease, filter .15s ease;
          }
          .hero .cta:hover {
            transform: translateY(-1px);
            filter: brightness(1.05);
          }

          /* --- Anchor offset per scroll --- */
          .anchor {
            position: relative;
            top: -80px;
            visibility: hidden;
          }

          /* --- Mobile tweaks --- */
          @media (max-width: 640px) {
            .hero {
              min-height: 60vh;
              padding: 3rem 1rem;
              margin-top: 56px;
            }
          }
          
        /* ===== SIDEBAR ULTRA-COMPATTA ===== */

        /* Padding interno container */
        [data-testid="stSidebar"] {
          padding: 6px 8px !important;
        }
        
        /* Spazio verticale minimo tra blocchi */
        [data-testid="stSidebar"] > div {
          margin-bottom: 6px !important;
        }
        
        /* Larghezza uniforme: quasi full width */
        [data-testid="stSidebar"] .stButton > button,
        [data-testid="stSidebar"] .stSelectbox > div,
        [data-testid="stSidebar"] .stMultiSelect > div,
        [data-testid="stSidebar"] .stTextInput > div,
        [data-testid="stSidebar"] .stNumberInput > div,
        [data-testid="stSidebar"] .stDateInput > div,
        [data-testid="stSidebar"] .stTimeInput > div,
        [data-testid="stSidebar"] .stTextArea > div,
        [data-testid="stSidebar"] .stSlider > div,
        [data-testid="stSidebar"] .stRadio,
        [data-testid="stSidebar"] .stCheckbox {
          width: 96% !important;
          margin: 0 auto !important;
        }
        
        /* Input/select/textarea: altezza e padding ridotti */
        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] select,
        [data-testid="stSidebar"] textarea {
          height: 34px !important;
          padding: 4px 8px !important;
          font-size: 13px !important;
          line-height: 1.2 !important;
          border-radius: 8px !important;
        }
        
        /* Textarea più alta ma compatta */
        [data-testid="stSidebar"] textarea {
          height: 72px !important;
          resize: vertical;
        }
        
        /* Bottoni compatti */
        [data-testid="stSidebar"] .stButton > button {
          padding: 6px 10px !important;
          min-height: 34px !important;
          font-size: 13px !important;
          border-radius: 10px !important;
        }
        
        /* Radio/checkbox: righe strette */
        [data-testid="stSidebar"] .stRadio > label,
        [data-testid="stSidebar"] .stCheckbox > label {
          display: block !important;
          padding: 4px 6px !important;
          border-radius: 8px;
          margin: 2px 0 !important;
          font-size: 13px !important;
        }
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label,
        [data-testid="stSidebar"] .stCheckbox > div {
          margin: 2px 0 !important;
        }
        
        /* Slider compatti */
        [data-testid="stSidebar"] .stSlider {
          padding: 2px 0 !important;
        }
        [data-testid="stSidebar"] .stSlider [data-baseweb="slider"] {
          margin: 2px 0 !important;
        }
        
        /* Titoli/separatori compatti */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
          margin: 6px 0 4px !important;
          font-size: 1rem !important;
        }
        [data-testid="stSidebar"] hr {
          margin: 6px 0 !important;
        }


        </style>
    """, unsafe_allow_html=True)



# --- SEZIONI ---
def show_hero():
    hero_html = """
    <section class="hero">
        <h1>FAi</h1>
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
        "- 🤝 Gestione clienti\n"
        "- 📅 Calendario e promemoria\n"
        "- 🤖 Automazioni smart per risparmiare tempo"
    )

def show_pricing():
    st.markdown('<span id="pricing" class="anchor"></span>', unsafe_allow_html=True)
    st.markdown("## 💰 Piani Tariffari")

    billing_cycle = st.radio("Fatturazione", ["Mensile", "Annuale"], horizontal=True)

    # Prezzi
    monthly = {"Free": 0, "Pro": 9.99, "Premium": 19.99}
    annual = {"Free": 0, "Pro": 99, "Premium": 199}  # scontati
    prices = monthly if billing_cycle == "Mensile" else annual

    # Funzionalità per piano
    features = [
        ("Fatture/mese", ["3", "Illimitate", "Illimitate"]),
        ("Invio email al cliente", ["✅", "✅", "✅"]),
        ("Invio PEC a SDI", ["❌", "✅", "✅"]),
        ("Calendario e promemoria", ["❌", "✅", "✅"]),
        ("Backup cloud", ["❌", "✅ settimanale", "✅ giornaliero"]),
        ("PEC personalizzata", ["❌", "❌", "✅"]),
        ("Supporto prioritario", ["❌", "❌", "✅"]),
        ("PDF personalizzati", ["❌", "❌", "✅"]),
        ("Statistiche avanzate", ["❌", "❌", "✅"]),
    ]

    # Header con pulsante Inizia
    cols = st.columns(3)
    piani = ["Free", "Pro", "Premium"]
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"### {piani[i]}")
            st.markdown(f"**€{prices[piani[i]]} /{'mese' if billing_cycle == 'Mensile' else 'anno'}**")
            st.markdown(f"[Inizia](#login)", unsafe_allow_html=True)

    # Tabella funzionalità
    st.markdown("### Funzionalità incluse")
    header_cols = st.columns([2, 1, 1, 1])
    with header_cols[0]:
        st.markdown("**Funzionalità**")
    for i in range(3):
        with header_cols[i + 1]:
            st.markdown(f"**{piani[i]}**")

    for label, vals in features:
        row_cols = st.columns([2, 1, 1, 1])
        with row_cols[0]:
            st.markdown(label)
        for i in range(3):
            with row_cols[i + 1]:
                st.markdown(vals[i])


def show_login():
    # ancora l’ancora #login è gestita dentro auth_block_on_landing
    auth_block_on_landing()

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
    st.markdown("<center class='muted'>© 2025 FAi</center>", unsafe_allow_html=True)

# --- ENTRYPOINT DELLA PAGINA ---
def show():
    inject_styles()
    show_hero()
    show_services()
    show_pricing()
    show_login()
    show_contacts()
    show_footer()
