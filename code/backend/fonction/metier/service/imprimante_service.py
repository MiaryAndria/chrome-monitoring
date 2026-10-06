from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.imprimante import get_liste_imprimante


def get_imprimante():
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_liste_imprimante(cur)
        cur.close()

        result = []
        for r in rows:
            result.append({
                "id":     r[0],
                "vid":    r[1],
                "pid":    r[2],
                "vendor": r[3],
                "nom":    r[4],
            })
        return result
    finally:
        close_connection(connexion)