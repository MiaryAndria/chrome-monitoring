from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.user.user import get_user_by_email
from backend.utils.password_hashage import verifier_password  

def login_user(email, mdp):
    if not email or not mdp:
        return None

    connexion = get_connection()
    if connexion is None:
        return None

    try:
        cur = connexion.cursor()
        user = get_user_by_email(cur, email)
        cur.close()

        if user is None:
            return None

        mot_de_passe_hache = user[3]  

        if not verifier_password(mdp, mot_de_passe_hache):
            return None
        return user
    finally:
        close_connection(connexion)