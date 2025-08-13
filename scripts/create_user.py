# scripts/create_test_users.py
from utils.auth import create_user

# Lista di tuple: (email, password, nome visualizzato)
USERS = [
    ("anna.rossi@fai.test",      "pass1234", "Anna Rossi"),
    ("luca.bianchi@fai.test",    "pass1234", "Luca Bianchi"),
    ("mario.verdi@fai.test",     "pass1234", "Mario Verdi"),
    ("giulia.neri@fai.test",     "pass1234", "Giulia Neri"),
    ("paolo.gallo@fai.test",     "pass1234", "Paolo Gallo"),
    ("chiara.fontana@fai.test",  "pass1234", "Chiara Fontana"),
    ("davide.moretti@fai.test",  "pass1234", "Davide Moretti"),
    ("francesca.greco@fai.test", "pass1234", "Francesca Greco"),
    ("matteo.romano@fai.test",   "pass1234", "Matteo Romano"),
    ("elisa.ferrari@fai.test",   "pass1234", "Elisa Ferrari"),
    ("max.tristi@fai.test",      "pass1234", "Max Tristi"),
    ("castcla@fai.test",         "pass1234", "Claudio Castiglione"),
    ("cosimo@fai.test",          "pass1234", "Cosimo Dini"),
    ("clelia@fai.test",          "pass1234", "Clelia Dini")
]

if __name__ == "__main__":
    for email, pwd, name in USERS:
        try:
            create_user(email, pwd, name)
            print(f"Creato utente: {email} ({name})")
        except Exception as e:
            print(f"Errore creazione {email}: {e}")
