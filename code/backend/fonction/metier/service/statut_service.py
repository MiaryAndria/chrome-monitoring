from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.statut import get_liste_statut

def getListeStatut():
    connexion = get_connection()
    if connexion is None :
        return None 
    cur = connexion.cursor()
    statut = get_liste_statut(cur)

    result = []

    for l in statut:
        result.append({
            "id": l[0],
            "nom": l[1]
        })
    
    close_connection(connexion)
    return result
# if __name__ == "__main__":
#     getListeStatut()