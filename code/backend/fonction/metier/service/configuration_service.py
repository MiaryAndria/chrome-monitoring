import json
from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.configuration import (
    get_liste_configuration,
    find_configurations_paginated,
    get_liste_archiver,
    find_configurations_archived_paginated,
    get_by_id_liste_archiver,
    get_configuration_by_id,
    insert_configuration,
    insert_configuration_statut,
    update_configuration,
    delete_configuration,
    restore_configuration,
)
from backend.utils.pagination import build_page
from backend.core.cache import cache_get, cache_set, cache_invalidate_prefix


def getListeConfiguration():
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_liste_configuration(cur)
        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "type": r[1] if r[1] is not None else None,
                "valeur": r[2],
                "date": r[3],
            })
        return result
    finally:
        close_connection(connexion)


def _fetch_configurations_page(page=1, page_size=10):
    connexion = get_connection()
    if connexion is None:
        return build_page([], 0, page, page_size)
    try:
        cur = connexion.cursor()
        rows = find_configurations_paginated(cur, page, page_size)
        total = rows[0][4] if rows else 0
        items = [
            {
                "id": r[0],
                "type": r[1] if r[1] is not None else None,
                "valeur": r[2],
                "date": r[3],
            }
            for r in rows
        ]
        cur.close()
        return build_page(items, total, page, page_size)
    finally:
        close_connection(connexion)


def _configurations_cache_key(page, page_size):
    return f"configurations:{page}:{page_size}"


def getConfigurationsPage(page=1, page_size=10):
    cle = _configurations_cache_key(page, page_size)
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    resultat = _fetch_configurations_page(page, page_size)
    return cache_set(cle, resultat)


def _fetch_configurations_archive_page(page=1, page_size=10):
    connexion = get_connection()
    if connexion is None:
        return build_page([], 0, page, page_size)
    try:
        cur = connexion.cursor()
        rows = find_configurations_archived_paginated(cur, page, page_size)
        total = rows[0][4] if rows else 0
        items = [
            {
                "id": r[0],
                "type": r[1] if r[1] is not None else None,
                "valeur": r[2],
                "date": r[3],
            }
            for r in rows
        ]
        cur.close()
        return build_page(items, total, page, page_size)
    finally:
        close_connection(connexion)


def getConfigurationsArchivePage(page=1, page_size=10):
    cle = f"configurations:archive:{page}:{page_size}"
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    resultat = _fetch_configurations_archive_page(page, page_size)
    return cache_set(cle, resultat)


def getDetailConfiguration(id_configuration):
    connexion = get_connection()
    if connexion is None:
        return None
    try:
        cur = connexion.cursor()
        row = get_configuration_by_id(cur, id_configuration)
        if row is None:
            return None 
        return{
            "id": row[0],
            "type": row[1] if row[1] is not None else None,
            "valeur": row[2],
            "date": row[3],   
        }
    finally:
        close_connection(connexion)

def UpdateConfiguration(id_configuration, type_, valeur, date=None, status_id=13):
    connexion = get_connection()
    if connexion is None:
        return False
    try:
        cur = connexion.cursor()
        updated_id = update_configuration(cur, id_configuration, type_, valeur, date)
        if updated_id is not None:
            insert_configuration_statut(cur, updated_id, status_id)
        connexion.commit()
        cache_invalidate_prefix("configurations:")
        return True
    except Exception:
        connexion.rollback()
        raise
    finally:
        close_connection(connexion)


def InsertConfiguration(type_, valeur, date=None, status_id=12):
    connexion = get_connection()
    if connexion is None:
        return None
    try:
        cur = connexion.cursor()
        id_configuration = insert_configuration(cur, type_, valeur, date)
        if id_configuration is not None:
            insert_configuration_statut(cur, id_configuration, status_id)
        connexion.commit()
        cache_invalidate_prefix("configurations:")
        return id_configuration
    except Exception:
        connexion.rollback()
        raise
    finally:
        close_connection(connexion)


def deleteConfiguration(id_configuration, status_id=14,date=None):
    connexion = get_connection()
    if connexion is None:
        return False
    try:
        cur = connexion.cursor()
        delete_configuration(cur, id_configuration, status_id,date)
        connexion.commit()
        cache_invalidate_prefix("configurations:")
        return True
    except Exception:
        connexion.rollback()
        raise
    finally:
        close_connection(connexion)


def getListeArchiveConfiguration():
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_liste_archiver(cur)
        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "type": r[1] if r[1] is not None else None,
                "valeur": r[2],
                "date": r[3],
            })
        return result
    finally:
        close_connection(connexion)


def reStaurer(id_configuration, status_id=16):
    connexion = get_connection()
    if connexion is None:
        return False
    try:
        cur = connexion.cursor()
        parametre = get_by_id_liste_archiver(cur, id_configuration)
        if parametre is None:
            return False

        restore_configuration(cur, id_configuration, status_id)
        connexion.commit()
        cache_invalidate_prefix("configurations:")
        return id_configuration
    except Exception:
        connexion.rollback()
        raise
    finally:
        close_connection(connexion)
