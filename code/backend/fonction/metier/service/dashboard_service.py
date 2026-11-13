from backend.fonction.conn.transaction import lecture
from backend.fonction.metier.repository.dashboard import get_summary as get_summary_repository
from backend.core.cache import cache_get, cache_set


DASHBOARD_CACHE_KEY = "dashboard:summary"


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
    with lecture() as cur:
        if cur is None:
            return dict(SUMMARY_VIDE)
        resume = get_summary_repository(cur)
        return resume if resume is not None else dict(SUMMARY_VIDE)


def get_summary():
    valeur = cache_get(DASHBOARD_CACHE_KEY)
    if valeur is not None:
        return valeur

    resultat = _fetch_summary()
    return cache_set(DASHBOARD_CACHE_KEY, resultat)
