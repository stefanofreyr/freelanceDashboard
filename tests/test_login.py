import bcrypt
from utils import db, auth

def test_login_ok_and_fail(temp_db):
    # Dati utente di test
    email = "login@example.com"
    password_ok = "Passw0rd!"
    password_fail = "WrongPass"

    # Crea hash bcrypt reale
    hashed_pw = bcrypt.hashpw(password_ok.encode("utf-8"), bcrypt.gensalt())

    # Registra utente nel DB
    db.create_user(email, hashed_pw, "Login Test")

    # Login corretto → deve tornare True
    assert auth.check_credentials(email, password_ok) is True, "Login corretto non riuscito"

    # Login errato → deve tornare False
    assert auth.check_credentials(email, password_fail) is False, "Login errato accettato"

    # Login con email inesistente → deve tornare False
    assert auth.check_credentials("altro@example.com", password_ok) is False, "Email inesistente accettata"
