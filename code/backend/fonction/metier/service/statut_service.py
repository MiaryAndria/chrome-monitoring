from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.statut import (
    get_liste_statut,
    get_liste_statut_all,
    find_statuts_paginated,
    get_statut_by_id,
    get_statut_by_name,
    update_statut,
)
from backend.core.cache import cache_get, cache_set, cache_invalidate_prefix
from backend.utils.pagination import build_page


def _statut_to_dict(row):
    return {
        "id": row[0],
        "nom": row[1],
    }


def getListeStatut():
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        statut = get_liste_statut(cur)
        return [_statut_to_dict(l) for l in statut]
    finally:
        close_connection(connexion)


def getListeStatutAll():
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        statut = get_liste_statut_all(cur)
        return [_statut_to_dict(l) for l in statut]
    finally:
        close_connection(connexion)


def _fetch_statuts_page(page=1, page_size=10):
    connexion = get_connection()
    if connexion is None:
        return build_page([], 0, page, page_size)
    try:
        cur = connexion.cursor()
        rows = find_statuts_paginated(cur, page, page_size)
        total = rows[0][2] if rows else 0
        items = [_statut_to_dict(r) for r in rows]
        cur.close()
        return build_page(items, total, page, page_size)
    finally:
        close_connection(connexion)


def getStatutsPage(page=1, page_size=10):
    cle = f"statuts:{page}:{page_size}"
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    return cache_set(cle, _fetch_statuts_page(page, page_size))


def getDetailStatut(id_statut):
    connexion = get_connection()
    if connexion is None:
        return None
    try:
        cur = connexion.cursor()
        row = get_statut_by_id(cur, id_statut)
        if row is None:
            return None
        return _statut_to_dict(row)
    finally:
        close_connection(connexion)


def UpdateStatut(id_statut, nom):
    nom = (nom or "").strip()
    if not nom:
        raise ValueError("Le nom du statut est obligatoire")

    connexion = get_connection()
    if connexion is None:
        raise ValueError("Erreur de connexion à la base de données")

    try:
        cur = connexion.cursor()
        existant = get_statut_by_name(cur, nom)
        if existant is not None and existant[0] != id_statut:
            cur.close()
            raise ValueError("Ce nom de statut existe déjà")

        updated_id = update_statut(cur, id_statut, nom)
        if updated_id is None:
            cur.close()
            raise ValueError("Statut introuvable")

        connexion.commit()
        cache_invalidate_prefix("statuts:")
        cache_invalidate_prefix("devices:")
        cache_invalidate_prefix("dashboard:")
        cur.close()
        return True
    except ValueError:
        connexion.rollback()
        raise
    except Exception:
        connexion.rollback()
        raise ValueError("Impossible de mettre à jour le statut")
    finally:
        close_connection(connexion)


# if __name__ == "__main__":
#     getListeStatut()
