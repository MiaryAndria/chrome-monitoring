from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.dashboard import get_summary as get_summary_repository


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
    "total_alerte": 0,
    "alerte_active": 0,
    "alerte_resolue": 0,
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
