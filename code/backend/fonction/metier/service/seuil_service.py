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
    hard_delete_seuil,
    get_type_seuil_by_categorie,
    get_categorie_seuil,
)
from backend.utils.pagination import build_page
from backend.core.cache import cache_get, cache_set, cache_invalidate_prefix


def _row_to_dict(row):
    return {
        "id": row[0],
        "id_type": row[1],
        "cle": row[2],
        "categorie": row[3],
        "valeur": row[4],
        "date": row[5],
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
        total = rows[0][6] if rows else 0
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
        total = rows[0][6] if rows else 0
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


def InsertSeuil(id_type, valeur, status_id=12):
    connexion = get_connection()
    if connexion is None:
        return None
    try:
        cur = connexion.cursor()
        id_seuil = insert_seuil(cur, id_type, valeur)
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


def UpdateSeuil(id_seuil, valeur, status_id=13):
    connexion = get_connection()
    if connexion is None:
        return False
    try:
        cur = connexion.cursor()
        updated_id = update_seuil(cur, id_seuil, valeur)
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


def hardDeleteSeuil(id_seuil):
    connexion = get_connection()
    if connexion is None:
        return False
    try:
        cur = connexion.cursor()
        supprime = hard_delete_seuil(cur, id_seuil)
        connexion.commit()
        cache_invalidate_prefix("seuils:")
        return supprime
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

def get_liste_type_seuil_by_categorie(id_categorie):
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_type_seuil_by_categorie(cur, id_categorie)
        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "type": r[1],
            })
        return result
    finally:
        close_connection(connexion)


def get_liste_categorie_seuil():
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_categorie_seuil(cur)
        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "categorie": r[1],
            })
        return result
    finally:
        close_connection(connexion)
