from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.seuil import (
    get_liste_seuil,
    find_seuils_paginated,
    get_liste_archiver,
    find_seuils_archived_paginated,
    get_by_id_liste_archiver,
    get_seuil_by_id,
    insert_seuil,
    insert_seuil_statut,
    update_seuil,
    delete_seuil,
    restore_seuil,
)
from backend.utils.pagination import build_page
from backend.core.cache import cache_get, cache_set, cache_invalidate_prefix


def _row_to_dict(row):
    return {
        "id": row[0],
        "cle": row[1] if row[1] is not None else None,
        "valeur": row[2],
        "date": row[3],
    }


def getListeSeuil():
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_liste_seuil(cur)
        return [_row_to_dict(r) for r in rows]
    finally:
        close_connection(connexion)


def _fetch_seuils_page(page=1, page_size=10):
    connexion = get_connection()
    if connexion is None:
        return build_page([], 0, page, page_size)
    try:
        cur = connexion.cursor()
        rows = find_seuils_paginated(cur, page, page_size)
        total = rows[0][4] if rows else 0
        items = [_row_to_dict(r) for r in rows]
        cur.close()
        return build_page(items, total, page, page_size)
    finally:
        close_connection(connexion)


def getSeuilsPage(page=1, page_size=10):
    cle = f"seuils:{page}:{page_size}"
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    resultat = _fetch_seuils_page(page, page_size)
    return cache_set(cle, resultat)


def _fetch_seuils_archive_page(page=1, page_size=10):
    connexion = get_connection()
    if connexion is None:
        return build_page([], 0, page, page_size)
    try:
        cur = connexion.cursor()
        rows = find_seuils_archived_paginated(cur, page, page_size)
        total = rows[0][4] if rows else 0
        items = [_row_to_dict(r) for r in rows]
        cur.close()
        return build_page(items, total, page, page_size)
    finally:
        close_connection(connexion)


def getSeuilsArchivePage(page=1, page_size=10):
    cle = f"seuils:archive:{page}:{page_size}"
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    resultat = _fetch_seuils_archive_page(page, page_size)
    return cache_set(cle, resultat)


def getListeArchiveSeuil():
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_liste_archiver(cur)
        return [_row_to_dict(r) for r in rows]
    finally:
        close_connection(connexion)


def getDetailSeuil(id_seuil):
    connexion = get_connection()
    if connexion is None:
        return None
    try:
        cur = connexion.cursor()
        row = get_seuil_by_id(cur, id_seuil)
        if row is None:
            return None
        return _row_to_dict(row)
    finally:
        close_connection(connexion)


def InsertSeuil(cle, valeur, status_id=12):
    connexion = get_connection()
    if connexion is None:
        return None
    try:
        cur = connexion.cursor()
        id_seuil = insert_seuil(cur, cle, valeur)
        if id_seuil is not None:
            insert_seuil_statut(cur, id_seuil, status_id)
        connexion.commit()
        cache_invalidate_prefix("seuils:")
        return id_seuil
    except Exception:
        connexion.rollback()
        raise
    finally:
        close_connection(connexion)


def UpdateSeuil(id_seuil, cle, valeur, status_id=13):
    connexion = get_connection()
    if connexion is None:
        return False
    try:
        cur = connexion.cursor()
        updated_id = update_seuil(cur, id_seuil, cle, valeur)
        if updated_id is not None:
            insert_seuil_statut(cur, updated_id, status_id)
        connexion.commit()
        cache_invalidate_prefix("seuils:")
        return True
    except Exception:
        connexion.rollback()
        raise
    finally:
        close_connection(connexion)


def deleteSeuil(id_seuil, status_id=14):
    connexion = get_connection()
    if connexion is None:
        return False
    try:
        cur = connexion.cursor()
        delete_seuil(cur, id_seuil, status_id)
        connexion.commit()
        cache_invalidate_prefix("seuils:")
        return True
    except Exception:
        connexion.rollback()
        raise
    finally:
        close_connection(connexion)


def reStaurer(id_seuil, status_id=16):
    connexion = get_connection()
    if connexion is None:
        return False
    try:
        cur = connexion.cursor()
        parametre = get_by_id_liste_archiver(cur, id_seuil)
        if parametre is None:
            return False

        restore_seuil(cur, id_seuil, status_id)
        connexion.commit()
        cache_invalidate_prefix("seuils:")
        return id_seuil
    except Exception:
        connexion.rollback()
        raise
    finally:
        close_connection(connexion)
