from backend.fonction.conn.transaction import lecture
from backend.fonction.metier.repository.utilisateur_google import (
    find_utilisateurs_recent_paginated,
    get_devices_by_utilisateur_recent,
)
from backend.utils.pagination import build_page
from backend.core.cache import cache_get, cache_set

MAX_DEVICES_PAR_UTILISATEUR = 100


def _utilisateur_to_dict(row):
    return {
        "id": row[0],
        "email": row[1],
        "nb_devices": row[2],
        "derniere_observation": str(row[3]) if row[3] else None,
        "filiales": list(row[4]) if row[4] else [],
    }


def _device_to_dict(row):
    return {
        "id": row[0],
        "device_id": row[1],
        "serial_number": row[2],
        "modele": row[3],
        "derniere_observation": str(row[4]) if row[4] else None,
    }


def _fetch_utilisateurs_recent_page(page, page_size, filiale, recherche):
    with lecture() as cur:
        if cur is None:
            return build_page([], 0, page, page_size)
        rows = find_utilisateurs_recent_paginated(cur, page, page_size, filiale, recherche)
        total = rows[0][5] if rows else 0
        items = [_utilisateur_to_dict(r) for r in rows]
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
        items = [_device_to_dict(r) for r in rows]
        return cache_set(cle, items)
