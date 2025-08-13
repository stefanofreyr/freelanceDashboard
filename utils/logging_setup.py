# utils/logging_setup.py
import logging
import os
from logging.handlers import RotatingFileHandler

class ContextFilter(logging.Filter):
    """
    Aggiunge user_id e user_email (se presenti in sessione) al record log,
    così ogni riga log è automaticamente contestualizzata.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        record.user_id = None
        record.user_email = None
        try:
            import streamlit as st
            u = st.session_state.get("user") or {}
            record.user_id = u.get("id")
            record.user_email = u.get("email")
        except Exception:
            # se Streamlit non è in esecuzione / fuori contesto, ignora
            pass
        return True

def _make_handler(path: str, level: int) -> RotatingFileHandler:
    os.makedirs("logs", exist_ok=True)
    handler = RotatingFileHandler(
        path, maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    fmt = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] user=%(user_email)s id=%(user_id)s %(message)s"
    )
    handler.setFormatter(fmt)
    handler.setLevel(level)
    handler.addFilter(ContextFilter())
    return handler

def setup_logging() -> None:
    """
    Inizializza due logger:
    - app  → logs/app.log (INFO+)
    - security → logs/security.log (INFO+)
    Protetto contro reinizializzazioni (Streamlit fa rerun).
    """
    # APP
    app_logger = logging.getLogger("app")
    if not app_logger.handlers:
        app_logger.setLevel(logging.INFO)
        app_logger.addHandler(_make_handler("logs/app.log", logging.INFO))
        app_logger.propagate = False

    # SECURITY
    sec_logger = logging.getLogger("security")
    if not sec_logger.handlers:
        sec_logger.setLevel(logging.INFO)
        sec_logger.addHandler(_make_handler("logs/security.log", logging.INFO))
        sec_logger.propagate = False

def get_app_logger() -> logging.Logger:
    return logging.getLogger("app")

def get_security_logger() -> logging.Logger:
    return logging.getLogger("security")
