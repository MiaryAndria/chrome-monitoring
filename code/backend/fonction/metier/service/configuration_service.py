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
    hard_delete_configuration,
    verifier_configuration_type_existe,
    get_type_configuration_by_categorie,
    get_categorie_configuration,
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


def getListeConfiguration():
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_liste_configuration(cur)
        return [_row_to_dict(r) for r in rows]
    finally:
        close_connection(connexion)


def _fetch_configurations_page(page=1, page_size=10, categorie=None):
    connexion = get_connection()
    if connexion is None:
        return build_page([], 0, page, page_size)
    try:
        cur = connexion.cursor()
        rows = find_configurations_paginated(cur, page, page_size, categorie)
        total = rows[0][6] if rows else 0
        items = [_row_to_dict(r) for r in rows]
        cur.close()
        return build_page(items, total, page, page_size)
    finally:
        close_connection(connexion)


def getConfigurationsPage(page=1, page_size=10, categorie=None):
    cle = f"configurations:{page}:{page_size}:{categorie}"
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    resultat = _fetch_configurations_page(page, page_size, categorie)
    return cache_set(cle, resultat)


def _fetch_configurations_archive_page(page=1, page_size=10):
    connexion = get_connection()
    if connexion is None:
        return build_page([], 0, page, page_size)
    try:
        cur = connexion.cursor()
        rows = find_configurations_archived_paginated(cur, page, page_size)
        total = rows[0][6] if rows else 0
        items = [_row_to_dict(r) for r in rows]
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


def getListeArchiveConfiguration():
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_liste_archiver(cur)
        return [_row_to_dict(r) for r in rows]
    finally:
        close_connection(connexion)


def getDetailConfiguration(id_configuration):
    connexion = get_connection()
    if connexion is None:
        return None
    try:
        cur = connexion.cursor()
        row = get_configuration_by_id(cur, id_configuration)
        if row is None:
            return None
        return _row_to_dict(row)
    finally:
        close_connection(connexion)


def InsertConfiguration(id_type, valeur, status_id=12):
    connexion = get_connection()
    if connexion is None:
        return None
    try:
        cur = connexion.cursor()
        existante = verifier_configuration_type_existe(cur, id_type)
        if existante is not None:
            raise ValueError(
                "Cette configuration existe déjà. Modifiez-la si vous voulez changer la valeur."
            )
        id_configuration = insert_configuration(cur, id_type, valeur)
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


def UpdateConfiguration(id_configuration, valeur, status_id=13):
    connexion = get_connection()
    if connexion is None:
        return False
    try:
        cur = connexion.cursor()
        updated_id = update_configuration(cur, id_configuration, valeur)
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


def deleteConfiguration(id_configuration, status_id=14):
    connexion = get_connection()
    if connexion is None:
        return False
    try:
        cur = connexion.cursor()
        delete_configuration(cur, id_configuration, status_id)
        connexion.commit()
        cache_invalidate_prefix("configurations:")
        return True
    except Exception:
        connexion.rollback()
        raise
    finally:
        close_connection(connexion)


def hardDeleteConfiguration(id_configuration):
    connexion = get_connection()
    if connexion is None:
        return False
    try:
        cur = connexion.cursor()
        supprime = hard_delete_configuration(cur, id_configuration)
        connexion.commit()
        cache_invalidate_prefix("configurations:")
        return supprime
    except Exception:
        connexion.rollback()
        raise
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


def get_liste_type_configuration_by_categorie(id_categorie):
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_type_configuration_by_categorie(cur, id_categorie)
        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "type": r[1],
            })
        return result
    finally:
        close_connection(connexion)


def get_liste_categorie_configuration():
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_categorie_configuration(cur)
        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "categorie": r[1],
            })
        return result
    finally:
        close_connection(connexion)
