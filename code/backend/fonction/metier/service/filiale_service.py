from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.filiale import get_liste_filiale
from backend.fonction.metier.repository.devices import (
    get_device_by_filiale,
    get_utilisateurs_by_device,
    get_historique_utilisateurs_device,
)
from backend.fonction.metier.repository.statut import get_status_actuel_device
from backend.fonction.metier.repository.utilisateur_google import get_utilisateur_by_id

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
        return []
    try:
        cur = connexion.cursor()
        devices = get_device_by_filiale(cur, id_filiale)
        
        result = []
        for d in devices:
            status = get_status_actuel_device(cur, d[0])
            utilisateurs = get_utilisateurs_by_device(cur, d[0])
            id_utilisateur = utilisateurs[0][0] if utilisateurs else None
            utilisateur_email = utilisateurs[0][1] if utilisateurs else "N/A"
            
            utilisateurs_recents = []
            historique = get_historique_utilisateurs_device(cur, d[0])
            if historique:
                for ur in historique:
                    if ur[2]:
                        ur_u = get_utilisateur_by_id(cur, ur[2])
                        if ur_u and ur_u[1] not in utilisateurs_recents:
                            utilisateurs_recents.append(ur_u[1])

            result.append({
                "id":               d[0],
                "id_device":        d[1],
                "serial_number":    d[2],
                "modele":           d[3],
                "id_type_appareil": d[4],
                "chromeos_version": d[5],
                "chrome_version":   d[6],
                "mac_adress":       d[7],
                "ip_adress":        d[8],
                "date":             str(d[9]) if d[9] else None,
                "id_utilisateur":   id_utilisateur,
                "status":           status,
                "utilisateur_email": utilisateur_email,
                "utilisateurs_recents": utilisateurs_recents,
            })

        cur.close()
        return result
    finally:
        close_connection(connexion)