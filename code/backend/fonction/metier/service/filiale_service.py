from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.filiale.filiale import (
    get_liste_filiale,
    get_filiale_by_id,
)
from backend.fonction.metier.repository.devices.devices import get_device_by_filiale
from backend.fonction.metier.repository.statut.statut import get_status_actuel_device
from backend.fonction.metier.repository.utilisateur_google.utilisateur import get_utilisateur_by_id
from backend.fonction.metier.repository.devices.device_utilisateur_recent import get_historique_utilisateurs_device

def get_all_filiales():

    connexion = get_connection()
    if connexion is None:
        return None
    try:
        cur = connexion.cursor()
        filiales = get_liste_filiale(cur)
        cur.close()
        return filiales
    finally:
        close_connection(connexion)


def get_devices_by_filiale(id_filiale: int):
    connexion = get_connection()
    if connexion is None:
        return None
    try:
        cur = connexion.cursor()
        devices = get_device_by_filiale(cur, id_filiale)
        
        result = []
        for d in devices:
            status = get_status_actuel_device(cur, d[0])
            utilisateur_email = "N/A"
            if d[5]:
                u = get_utilisateur_by_id(cur, d[5])
                if u:
                    utilisateur_email = u[1] 
            
            utilisateurs_recents = []
            historique = get_historique_utilisateurs_device(cur, d[0])
            if historique:
                for ur in historique:
                    if ur[2]:
                        ur_u = get_utilisateur_by_id(cur, ur[2])
                        if ur_u and ur_u[1] not in utilisateurs_recents:
                            utilisateurs_recents.append(ur_u[1])

            result.append(
                (d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8], d[9], d[10], status, utilisateur_email, utilisateurs_recents)
            )

        cur.close()
        return result
    finally:
        close_connection(connexion)