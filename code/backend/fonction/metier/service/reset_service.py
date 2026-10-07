from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.devices import delete_all

def reset_data():
    connexion = get_connection()
    if connexion is None:
        print("Connexion BDD impossible")
        return None

    cur = connexion.cursor()
    try:
        delete_all(cur)
        connexion.commit()
        return True
    finally:
        close_connection(connexion)
