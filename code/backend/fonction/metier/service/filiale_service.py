from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.filiale import (
    get_liste_filiale,
    find_filiales_paginated,
)
from backend.fonction.metier.service.device_service import getDevicesPage
from backend.utils.pagination import build_page
from backend.core.cache import cache_get, cache_set


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


def _fetch_filiales_page(page=1, page_size=10, recherche=None):
    connexion = get_connection()
    if connexion is None:
        return build_page([], 0, page, page_size)
    try:
        cur = connexion.cursor()
        rows = find_filiales_paginated(cur, page, page_size, recherche)
        total = rows[0]["total"] if rows else 0
        items = [
            {"id": row["id"], "org_unit_path": row["org_unit_path"]}
            for row in rows
        ]
        cur.close()
        return build_page(items, total, page, page_size)
    finally:
        close_connection(connexion)


def _filiales_cache_key(page, page_size, recherche):
    return f"filiales:{page}:{page_size}:{recherche}"


def get_filiales_page(page=1, page_size=10, recherche=None):
    cle = _filiales_cache_key(page, page_size, recherche)
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    resultat = _fetch_filiales_page(page, page_size, recherche)
    return cache_set(cle, resultat)


def get_devices_by_filiale(id_filiale, page=1, page_size=10, statut=None,
                           type_appareil=None, modele=None, recherche=None,
                           datetime_from=None, datetime_to=None):
    return getDevicesPage(
        page=page,
        page_size=page_size,
        id_filiale=id_filiale,
        statut=statut,
        type_appareil=type_appareil,
        modele=modele,
        recherche=recherche,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
    )
