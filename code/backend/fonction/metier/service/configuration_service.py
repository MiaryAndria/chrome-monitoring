from backend.fonction.conn.transaction import lecture, transaction
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
from backend.fonction.metier.repository.statut.constants import (
    ID_STATUT_CREER,
    ID_STATUT_MODIFIER,
    ID_STATUT_SUPPRIMER,
    ID_STATUT_RESTAURER,
)

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
    with lecture() as cur:
        if cur is None:
            return []
        return [_row_to_dict(r) for r in get_liste_configuration(cur)]

def _fetch_configurations_page(page=1, page_size=10, categorie=None):
    with lecture() as cur:
        if cur is None:
            return build_page([], 0, page, page_size)
        rows = find_configurations_paginated(cur, page, page_size, categorie)
        total = rows[0][6] if rows else 0
        items = [_row_to_dict(r) for r in rows]
        return build_page(items, total, page, page_size)


def getConfigurationsPage(page=1, page_size=10, categorie=None):
    cle = f"configurations:{page}:{page_size}:{categorie}"
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    resultat = _fetch_configurations_page(page, page_size, categorie)
    return cache_set(cle, resultat)


def _fetch_configurations_archive_page(page=1, page_size=10):
    with lecture() as cur:
        if cur is None:
            return build_page([], 0, page, page_size)
        rows = find_configurations_archived_paginated(cur, page, page_size)
        total = rows[0][6] if rows else 0
        items = [_row_to_dict(r) for r in rows]
        return build_page(items, total, page, page_size)


def getConfigurationsArchivePage(page=1, page_size=10):
    cle = f"configurations:archive:{page}:{page_size}"
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    resultat = _fetch_configurations_archive_page(page, page_size)
    return cache_set(cle, resultat)


def getListeArchiveConfiguration():
    with lecture() as cur:
        if cur is None:
            return []
        return [_row_to_dict(r) for r in get_liste_archiver(cur)]


def getDetailConfiguration(id_configuration):
    with lecture() as cur:
        if cur is None:
            return None
        row = get_configuration_by_id(cur, id_configuration)
        if row is None:
            return None
        return _row_to_dict(row)


def InsertConfiguration(id_type, valeur):
    with transaction() as cur:
        if cur is None:
            return None
        if verifier_configuration_type_existe(cur, id_type) is not None:
            raise ValueError(
                "Cette configuration existe déjà. Modifiez-la si vous voulez changer la valeur."
            )
        id_configuration = insert_configuration(cur, id_type, valeur)
        if id_configuration is not None:
            insert_configuration_statut(cur, id_configuration, ID_STATUT_CREER)
    cache_invalidate_prefix("configurations:")
    return id_configuration


def UpdateConfiguration(id_configuration, valeur):
    with transaction() as cur:
        if cur is None:
            return False
        updated_id = update_configuration(cur, id_configuration, valeur)
        if updated_id is not None:
            insert_configuration_statut(cur, updated_id, ID_STATUT_MODIFIER)
    cache_invalidate_prefix("configurations:")
    return True


def deleteConfiguration(id_configuration):
    with transaction() as cur:
        if cur is None:
            return False
        delete_configuration(cur, id_configuration, ID_STATUT_SUPPRIMER)
    cache_invalidate_prefix("configurations:")
    return True


def hardDeleteConfiguration(id_configuration):
    with transaction() as cur:
        if cur is None:
            return False
        supprime = hard_delete_configuration(cur, id_configuration)
    cache_invalidate_prefix("configurations:")
    return supprime


def reStaurer(id_configuration):
    with transaction() as cur:
        if cur is None:
            return False
        if get_by_id_liste_archiver(cur, id_configuration) is None:
            return False
        restore_configuration(cur, id_configuration, ID_STATUT_RESTAURER)
    cache_invalidate_prefix("configurations:")
    return id_configuration


def get_liste_type_configuration_by_categorie(id_categorie):
    with lecture() as cur:
        if cur is None:
            return []
        rows = get_type_configuration_by_categorie(cur, id_categorie)
        return [
            {
                "id": r[0],
                "type": r[1],
            }
            for r in rows
        ]


def get_liste_categorie_configuration():
    with lecture() as cur:
        if cur is None:
            return []
        rows = get_categorie_configuration(cur)
        return [
            {
                "id": r[0],
                "categorie": r[1],
            }
            for r in rows
        ]
