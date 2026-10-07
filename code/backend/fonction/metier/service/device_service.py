from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.devices import (
    get_device_by_id,
    get_device_by_device_id,
    get_liste_device,
    recherche_multicritere,
)
from backend.utils.builder import _build_device_response

def getListeDevice():
    connexion = get_connection()
    if connexion is None:
        print("Connexion BDD impossible")
        return []
    cur = connexion.cursor()
    try:
        devices = get_liste_device(cur)
        return [payload for d in devices if (payload := _build_device_response(cur, d)) is not None]
    finally:
        close_connection(connexion)

def getDeviceDetail(id):
    connexion = get_connection()
    if connexion is None:
        print("Connexion BDD IMPOSSIBLE")
        return None
    try:
        cur = connexion.cursor()
        d = get_device_by_id(cur, id)
        return _build_device_response(cur, d)
    finally:
        close_connection(connexion)


def getDeviceFiltered(recherche):
    connexion = get_connection()
    if connexion is None:
        print("Connexion BDD IMPOSSIBLE")
        return []
    try:
        cur = connexion.cursor()
        devices = recherche_multicritere(cur, recherche)
        if not devices:
            return []

        result = []
        for d in devices:
            payload = _build_device_response(cur, get_device_by_id(cur, d[0]))
            if payload:
                result.append(payload)
        return result
    finally:
        close_connection(connexion)
        
# if __name__ == "__main__":
#     connexion = get_connection()
#     cur = connexion.cursor()
#     # device = recherche_multicritere(cur,'digital.salamander@taloumis.mg')
#     # device = getDeviceDetail(2)
#     print(device)
