from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.devices import (
    get_device_by_id,
    get_device_by_device_id,
    get_liste_device,
    get_liste_modele,
    get_all_device_stats,
    recherche_multicritere,
    find_devices_paginated,
)
from backend.utils.builder import _build_device_response, _serialize_device_row
from backend.utils.format_valeur import format_bytes, format_frequency
from backend.utils.pagination import build_page
from backend.core.cache import cache_get, cache_set

def getListeDevice():
    connexion = get_connection()
    if connexion is None:
        print("Connexion BDD impossible")
        return []
    cur = connexion.cursor()
    try:
        devices = get_liste_device(cur)
        return [payload for d in devices if (payload := _build_device_response(cur, d)) is not None]
    finally:
        close_connection(connexion)

def getDeviceDetail(id):
    connexion = get_connection()
    if connexion is None:
        print("Connexion BDD IMPOSSIBLE")
        return None
    try:
        cur = connexion.cursor()
        d = get_device_by_id(cur, id)
        return _build_device_response(cur, d)
    finally:
        close_connection(connexion)


def getDeviceFiltered(recherche):
    connexion = get_connection()
    if connexion is None:
        print("Connexion BDD IMPOSSIBLE")
        return []
    try:
        cur = connexion.cursor()
        devices = recherche_multicritere(cur, recherche)
        if not devices:
            return []

        result = []
        for d in devices:
            payload = _build_device_response(cur, get_device_by_id(cur, d[0]))
            if payload:
                result.append(payload)
        return result
    finally:
        close_connection(connexion)


def _fetch_devices_page(page=1, page_size=10, id_filiale=None, filiale=None,
                        id_statut=None, statut=None, type_appareil=None, recherche=None,
                        datetime_from=None, datetime_to=None,modele=None,utilisateur_recent=None):
    connexion = get_connection()
    if connexion is None:
        return build_page([], 0, page, page_size)
    try:
        cur = connexion.cursor()
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
        cur.close()
        return build_page(items, total, page, page_size)
    finally:
        close_connection(connexion)


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

    connexion = get_connection()
    if connexion is None:
        return {"total": 0, "actifs": 0}
    try:
        cur = connexion.cursor()
        resultat = get_all_device_stats(cur)
        cur.close()
        return cache_set(DEVICE_STATS_CACHE_KEY, resultat, DEVICE_STATS_CACHE_TTL)
    finally:
        close_connection(connexion)


def get_modeles():
    valeur = cache_get(MODELES_CACHE_KEY)
    if valeur is not None:
        return valeur

    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_liste_modele(cur)
        cur.close()
        return cache_set(MODELES_CACHE_KEY, rows, MODELES_CACHE_TTL)
    finally:
        close_connection(connexion)


        
# if __name__ == "__main__":
#     connexion = get_connection()
#     cur = connexion.cursor()
#     # device = recherche_multicritere(cur,'digital.salamander@taloumis.mg')
#     # device = getDeviceDetail(2)
#     print(device)
