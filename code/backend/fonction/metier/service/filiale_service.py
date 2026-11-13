from backend.fonction.conn.transaction import lecture
from backend.fonction.metier.repository.filiale import (
    get_liste_filiale,
    find_filiales_paginated,
    get_filiale_device_stats,
)
from backend.fonction.metier.service.device_service import getDevicesPage
from backend.utils.pagination import build_page
from backend.core.cache import cache_get, cache_set


def get_all_filiales():
    with lecture() as cur:
        if cur is None:
            return None
        return get_liste_filiale(cur)


def _fetch_filiales_page(page=1, page_size=10, recherche=None):
    with lecture() as cur:
        if cur is None:
            return build_page([], 0, page, page_size)
        rows = find_filiales_paginated(cur, page, page_size, recherche)
        total = rows[0]["total"] if rows else 0
        items = [
            {"id": row["id"], "org_unit_path": row["org_unit_path"]}
            for row in rows
        ]
        return build_page(items, total, page, page_size)


def _filiales_cache_key(page, page_size, recherche):
    return f"filiales:{page}:{page_size}:{recherche}"


def get_filiales_page(page=1, page_size=10, recherche=None):
    cle = _filiales_cache_key(page, page_size, recherche)
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    resultat = _fetch_filiales_page(page, page_size, recherche)
    return cache_set(cle, resultat)


def get_devices_by_filiale(id_filiale, page=1, page_size=10, id_statut=None, statut=None,
                           type_appareil=None, modele=None, recherche=None,
                           utilisateur_recent=None,
                           datetime_from=None, datetime_to=None):
    return getDevicesPage(
        page=page,
        page_size=page_size,
        id_filiale=id_filiale,
        id_statut=id_statut,
        statut=statut,
        type_appareil=type_appareil,
        modele=modele,
        recherche=recherche,
        utilisateur_recent=utilisateur_recent,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
    )


def get_filiale_stats(id_filiale):
    cle = f"filiales:stats:{id_filiale}"
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    with lecture() as cur:
        if cur is None:
            return {"total": 0, "actifs": 0}
        resultat = get_filiale_device_stats(cur, id_filiale)
        return cache_set(cle, resultat)
