from backend.fonction.conn.connexion import get_connection, close_connection

from backend.fonction.metier.repository.devices import (
    get_nombre_device, get_device_by_type, get_device_by_statut, get_liste_type_appareil
)
from backend.fonction.metier.repository.statut import get_liste_statut

def nombreDevice(cur):
    return get_nombre_device(cur)

def nombreDeviceByType(cur):
    lt = get_liste_type_appareil(cur)
    result = {}
    for l in lt:
        id_type=l[0]
        nom_type=l[1]
        typebydevice = get_device_by_type(cur, id_type)
        nombre = len(typebydevice)
        result[nom_type] = nombre
    return result

def nombreDeviceByStatut(cur):
    ls = get_liste_statut(cur)
    result = {}
    for l in ls:
        id_statut = l[0]
        nom_statut = l[1]
        statutbydevice = get_device_by_statut(cur, id_statut)
        nombre = len(statutbydevice)
        result[nom_statut]=nombre
    return result

def getStatistiques():
    connexion = get_connection()
    if connexion is None:
        return None
    try:
        cur = connexion.cursor()
        n = nombreDevice(cur)
        l = nombreDeviceByStatut(cur)
        nt = nombreDeviceByType(cur)

        return {
            "total": n,
            "par_statut": l,
            "par_type": nt
        }

    finally:
        close_connection(connexion)
        
    