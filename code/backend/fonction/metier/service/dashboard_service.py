from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.dashboard import get_summary as get_summary_repository
from backend.fonction.metier.repository.devices import (
    get_nombre_device,
    get_device_by_type,
    get_device_by_statut,
    get_liste_type_appareil,
)
from backend.fonction.metier.repository.statut import get_liste_statut
STATUTS_DASHBOARD = {"ACTIVE", "DELINQUENT", "DISABLED", "DEPROVISIONED"}

SUMMARY_VIDE = {
    "nb_total_appareils": 0,
    "nb_actifs": 0,
    "nb_indisponibles": 0,
    "nb_anomalie": 0,
    "nb_reparation": 0,
    "nb_crashs": 0,
    "nb_incidents": 0,
    "nb_imprimantes": 0,
    "repartition_statuts": {},
    "repartition_types": {},
    "repartition_evenements": {},
}


def _fetch_summary():
    connexion = get_connection()
    if connexion is None:
        return dict(SUMMARY_VIDE)
    try:
        cur = connexion.cursor()
        resume = get_summary_repository(cur)
        cur.close()
        return resume if resume is not None else dict(SUMMARY_VIDE)
    finally:
        close_connection(connexion)


def get_summary():
    return _fetch_summary()


def nombreDevice(cur):
    return get_nombre_device(cur)


def nombreDeviceByType(cur):
    liste_types = get_liste_type_appareil(cur)
    result = {}
    for ligne in liste_types:
        id_type = ligne[0]
        nom_type = ligne[1]
        type_by_device = get_device_by_type(cur, id_type)
        result[nom_type] = len(type_by_device)
    return result


def nombreDeviceByStatut(cur):
    liste_statuts = get_liste_statut(cur)
    result = {}
    for ligne in liste_statuts:
        id_statut = ligne[0]
        nom_statut = ligne[1]
        if nom_statut not in STATUTS_DASHBOARD:
            continue
        statut_by_device = get_device_by_statut(cur, id_statut)
        result[nom_statut] = len(statut_by_device)
    return result


def getStatistiques():
    connexion = get_connection()
    if connexion is None:
        return None
    try:
        cur = connexion.cursor()
        total = nombreDevice(cur)
        par_statut = nombreDeviceByStatut(cur)
        par_type = nombreDeviceByType(cur)

        return {
            "total": total,
            "par_statut": par_statut,
            "par_type": par_type,
        }
    finally:
        close_connection(connexion)


__all__ = [
    "get_summary",
    "getStatistiques",
]
