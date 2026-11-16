from backend.fonction.conn.transaction import lecture
from backend.fonction.metier.repository.imprimante import (
    get_liste_imprimante,
    get_liste_vendor,
    get_imprimante_by_id,
    get_utilisateurs_by_imprimante,
    get_devices_by_imprimante,
    find_imprimantes_paginated,
)
from backend.utils.pagination import build_page
from backend.core.cache import cache_get, cache_set
from backend.exceptions import AppError


def get_imprimante():
    with lecture() as cur:
        if cur is None:
            return []
        rows = get_liste_imprimante(cur)
        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "vid": r[1],
                "pid": r[2],
                "vendor": r[3],
                "nom": r[4],
            })
        return result

def get_vendors():
    with lecture() as cur:
        if cur is None:
            return []
        return get_liste_vendor(cur)


def get_imprimante_detail(id_imprimante: int):
    with lecture() as cur:
        if cur is None:
            raise AppError("Connexion à la base impossible", status_code=503)

        r = get_imprimante_by_id(cur, id_imprimante)
        if r is None:
            return None

        devices = get_devices_by_imprimante(cur, id_imprimante)
        users = get_utilisateurs_by_imprimante(cur, id_imprimante)

        return {
            "id": r[0],
            "vid": r[1],
            "pid": r[2],
            "vendor": r[3],
            "nom": r[4],
            "device": devices,
            "user": users,
        }


def _fetch_imprimantes_page(page=1, page_size=10, recherche=None, vendor=None,
                            datetime_from=None, datetime_to=None):
    with lecture() as cur:
        if cur is None:
            return build_page([], 0, page, page_size)
        rows, total = find_imprimantes_paginated(
            cur, page, page_size, recherche, vendor, datetime_from, datetime_to
        )
        items = []
        for row in rows:
            items.append({
                "id": row["id"],
                "vid": row["vid"],
                "pid": row["pid"],
                "vendor": row["vendor"],
                "nom": row["nom"],
            })
        return build_page(items, total, page, page_size)


def _imprimantes_cache_key(page, page_size, recherche, vendor, datetime_from,
                           datetime_to):
    return (
        f"imprimantes:{page}:{page_size}:{recherche}:{vendor}:"
        f"{datetime_from}:{datetime_to}"
    )


def get_imprimantes_page(page=1, page_size=10, recherche=None, vendor=None,
                         datetime_from=None, datetime_to=None):
    cle = _imprimantes_cache_key(
        page, page_size, recherche, vendor, datetime_from, datetime_to
    )
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    resultat = _fetch_imprimantes_page(
        page, page_size, recherche, vendor, datetime_from, datetime_to
    )
    return cache_set(cle, resultat)
