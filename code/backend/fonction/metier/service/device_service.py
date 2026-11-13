from backend.fonction.conn.transaction import lecture
from backend.fonction.metier.repository.devices import (
    get_device_detail,
    get_liste_modele,
    get_all_device_stats,
    find_devices_paginated,
)
from backend.utils.builder import _serialize_device_row
from backend.utils.pagination import build_page
from backend.core.cache import cache_get, cache_set

def getDeviceDetail(id):
    with lecture() as cur:
        if cur is None:
            print("Connexion BDD IMPOSSIBLE")
            return None
        row = get_device_detail(cur, id)
        return _serialize_device_row(row) if row else None


def _fetch_devices_page(page=1, page_size=10, id_filiale=None, filiale=None,
                        id_statut=None, statut=None, type_appareil=None, recherche=None,
                        datetime_from=None, datetime_to=None,modele=None,utilisateur_recent=None):
    with lecture() as cur:
        if cur is None:
            return build_page([], 0, page, page_size)
        rows = find_devices_paginated(
            cur, page, page_size,
            id_filiale=id_filiale, filiale=filiale, id_statut=id_statut, statut=statut,
            type_appareil=type_appareil, recherche=recherche,
            datetime_from=datetime_from, datetime_to=datetime_to,
            modele=modele, utilisateur_recent=utilisateur_recent
        )
        total = rows[0]["total"] if rows else 0
        # Page vide (page au-dela de la derniere) : le COUNT(*) OVER() n'est plus dispo,
        # on refait une sonde page 1 pour recuperer le vrai total.
        if not rows and page > 1:
            sonde = find_devices_paginated(
                cur, 1, 1,
                id_filiale=id_filiale, filiale=filiale, id_statut=id_statut, statut=statut,
                type_appareil=type_appareil, recherche=recherche,
                datetime_from=datetime_from, datetime_to=datetime_to,
                modele=modele, utilisateur_recent=utilisateur_recent
            )
            total = sonde[0]["total"] if sonde else 0
        items = []
        for row in rows:
            items.append(_serialize_device_row(row))
        return build_page(items, total, page, page_size)


def _devices_cache_key(page, page_size, id_filiale, filiale, id_statut, statut,
                       type_appareil, recherche, datetime_from, datetime_to,modele,utilisateur_recent):
    return (
        f"devices:{page}:{page_size}:{id_filiale}:{filiale}:{utilisateur_recent}:"
        f"{id_statut}:{statut}:{type_appareil}:{recherche}:{datetime_from}:{datetime_to}:{modele}"
    )


def getDevicesPage(page=1, page_size=10, id_filiale=None, filiale=None,
                   id_statut=None, statut=None, type_appareil=None, recherche=None,
                   datetime_from=None, datetime_to=None, modele=None,utilisateur_recent=None):
    cle = _devices_cache_key(
        page, page_size, id_filiale, filiale, id_statut, statut, type_appareil,
        recherche, datetime_from, datetime_to, modele,utilisateur_recent
    )
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    resultat = _fetch_devices_page(
        page, page_size, id_filiale, filiale, id_statut, statut, type_appareil,
        recherche, datetime_from, datetime_to, modele,utilisateur_recent
    )
    return cache_set(cle, resultat)


MODELES_CACHE_KEY = "devices:modeles"
MODELES_CACHE_TTL = 300

DEVICE_STATS_CACHE_KEY = "devices:stats:all"
DEVICE_STATS_CACHE_TTL = 60


def get_device_stats():
    valeur = cache_get(DEVICE_STATS_CACHE_KEY)
    if valeur is not None:
        return valeur

    with lecture() as cur:
        if cur is None:
            return {"total": 0, "actifs": 0}
        resultat = get_all_device_stats(cur)
        return cache_set(DEVICE_STATS_CACHE_KEY, resultat, DEVICE_STATS_CACHE_TTL)


def get_modeles():
    valeur = cache_get(MODELES_CACHE_KEY)
    if valeur is not None:
        return valeur

    with lecture() as cur:
        if cur is None:
            return []
        rows = get_liste_modele(cur)
        return cache_set(MODELES_CACHE_KEY, rows, MODELES_CACHE_TTL)

