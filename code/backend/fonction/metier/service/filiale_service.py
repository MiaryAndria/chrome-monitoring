from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.filiale import get_liste_filiale
from backend.fonction.metier.service.device_service import getDevicesPage


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


def get_devices_by_filiale(id_filiale, page=1, page_size=10, statut=None,
                           datetime_from=None, datetime_to=None):
    return getDevicesPage(
        page=page,
        page_size=page_size,
        id_filiale=id_filiale,
        statut=statut,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
    )
