from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.imprimante import (
    get_liste_imprimante,
    get_imprimante_by_id,
    get_utilisateurs_by_imprimante,
    get_devices_by_imprimante,
    find_imprimantes_paginated,
)
from backend.utils.pagination import build_page
from backend.core.cache import cache_get, cache_set


def get_imprimante():
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_liste_imprimante(cur)
        cur.close()
        return [
            {"id": r[0], "vid": r[1], "pid": r[2], "vendor": r[3], "nom": r[4]}
            for r in rows
        ]
    finally:
        close_connection(connexion)


def get_imprimante_detail(id_imprimante: int):
    connexion = get_connection()
    if connexion is None:
        raise Exception("Connexion à la base impossible")
    try:
        cur = connexion.cursor()

        r = get_imprimante_by_id(cur, id_imprimante)
        if r is None:
            return None

        devices = get_devices_by_imprimante(cur, id_imprimante)
        users = get_utilisateurs_by_imprimante(cur, id_imprimante)
        cur.close()

        return {
            "id": r[0],
            "vid": r[1],
            "pid": r[2],
            "vendor": r[3],
            "nom": r[4],
            "device": devices,
            "user": users,
        }
    finally:
        close_connection(connexion)


def _fetch_imprimantes_page(page=1, page_size=10, recherche=None,
                            datetime_from=None, datetime_to=None):
    connexion = get_connection()
    if connexion is None:
        return build_page([], 0, page, page_size)
    try:
        cur = connexion.cursor()
        rows = find_imprimantes_paginated(
            cur, page, page_size, recherche, datetime_from, datetime_to
        )
        total = rows[0]["total"] if rows else 0
        items = [
            {
                "id": row["id"],
                "vid": row["vid"],
                "pid": row["pid"],
                "vendor": row["vendor"],
                "nom": row["nom"],
            }
            for row in rows
        ]
        cur.close()
        return build_page(items, total, page, page_size)
    finally:
        close_connection(connexion)


def _imprimantes_cache_key(page, page_size, recherche, datetime_from,
                           datetime_to):
    return (
        f"imprimantes:{page}:{page_size}:{recherche}:"
        f"{datetime_from}:{datetime_to}"
    )


def get_imprimantes_page(page=1, page_size=10, recherche=None,
                         datetime_from=None, datetime_to=None):
    cle = _imprimantes_cache_key(
        page, page_size, recherche, datetime_from, datetime_to
    )
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    resultat = _fetch_imprimantes_page(
        page, page_size, recherche, datetime_from, datetime_to
    )
    return cache_set(cle, resultat)