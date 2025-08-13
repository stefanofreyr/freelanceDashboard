import streamlit as st
import requests
import os

def show():
    st.title("💬 Assistente AI (Groq)")

    # API key
    groq_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    if not groq_key:
        st.error("⚠️ Manca GROQ_API_KEY nei secrets. Aggiungila per usare questa funzione.")
        return

    # Inizializza chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "system", "content": "Sei un assistente AI che risponde in italiano, in modo chiaro e utile."}
        ]

    # Selezione modello
    model_choice = st.selectbox(
        "Modello Groq",
        ["llama3-8b-8192", "llama3-70b-8192"],
        index=0
    )

    # Input utente
    user_input = st.text_area("Scrivi un messaggio:", height=80)

    if st.button("Invia") and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model_choice,
                "messages": st.session_state.chat_history,
                "temperature": 0.7,
                "max_tokens": 800
            }
            r = requests.post(url, headers=headers, json=payload, timeout=60)
            r.raise_for_status()
            reply = r.json()["choices"][0]["message"]["content"].strip()

            st.session_state.chat_history.append({"role": "assistant", "content": reply})

        except requests.exceptions.RequestException as e:
            st.error(f"Errore nella chiamata Groq: {e}")

    # Mostra conversazione
    for msg in st.session_state.chat_history[1:]:  # salta il system
        if msg["role"] == "user":
            st.markdown(f"**👤 Tu:** {msg['content']}")
        else:
            st.markdown(f"**🤖 AI:** {msg['content']}")

    # Pulsante per resettare
    if st.button("🔄 Nuova conversazione"):
        st.session_state.chat_history = [
            {"role": "system", "content": "Sei un assistente AI che risponde in italiano, in modo chiaro e utile."}
        ]
