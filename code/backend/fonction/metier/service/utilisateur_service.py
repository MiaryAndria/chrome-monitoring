from backend.fonction.conn.transaction import lecture
from backend.fonction.metier.repository import (
    find_utilisateurs_recent_paginated,
    get_devices_by_utilisateur_recent,
)
from backend.utils.pagination import build_page
from backend.core.cache import cache_get, cache_set

MAX_DEVICES_PAR_UTILISATEUR = 100


def _fetch_utilisateurs_recent_page(page, page_size, filiale, recherche):
    with lecture() as cur:
        if cur is None:
            return build_page([], 0, page, page_size)
        rows, total = find_utilisateurs_recent_paginated(cur, page, page_size, filiale, recherche)
        items = []
        for r in rows:
            items.append({
                "id": r[0],
                "email": r[1],
                "nb_devices": r[2],
                "derniere_observation": str(r[3]) if r[3] else None,
                "filiales": list(r[4]) if r[4] else [],
            })
        return build_page(items, total, page, page_size)


def get_utilisateurs_recent_page(page=1, page_size=10, filiale=None, recherche=None):
    cle = f"utilisateurs:{page}:{page_size}:{filiale}:{recherche}"
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    resultat = _fetch_utilisateurs_recent_page(page, page_size, filiale, recherche)
    return cache_set(cle, resultat)


def get_utilisateur_recent_devices(id_utilisateur, limit=MAX_DEVICES_PAR_UTILISATEUR):
    cle = f"utilisateurs:devices:{id_utilisateur}:{limit}"
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    with lecture() as cur:
        if cur is None:
            return []
        rows = get_devices_by_utilisateur_recent(cur, id_utilisateur, limit)
        items = []
        for r in rows:
            items.append({
                "id": r[0],
                "device_id": r[1],
                "serial_number": r[2],
                "modele": r[3],
                "derniere_observation": str(r[4]) if r[4] else None,
            })
        return cache_set(cle, items)

    
