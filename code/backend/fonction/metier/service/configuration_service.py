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
    get_type_configuration_by_id,
    get_type_configuration_by_categorie,
    get_categorie_configuration,
)
from backend.utils.pagination import build_page
from backend.core.cache import cache_get, cache_set, cache_invalidate_prefix
from backend.fonction.metier.repository.statut import (
    ID_STATUT_CREER,
    ID_STATUT_MODIFIER,
    ID_STATUT_SUPPRIMER,
    ID_STATUT_RESTAURER,
)
from backend.exceptions import ValidationError, NotFoundError, ConflictError

def getListeConfiguration():
    with lecture() as cur:
        if cur is None:
            return []
        rows = get_liste_configuration(cur)
        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "id_type": r[1],
                "cle": r[2],
                "categorie": r[3],
                "valeur": r[4],
                "date": r[5],
            })
        return result

def _fetch_configurations_page(page=1, page_size=10, categorie=None):
    with lecture() as cur:
        if cur is None:
            return build_page([], 0, page, page_size)
        rows, total = find_configurations_paginated(cur, page, page_size, categorie)
        items = []
        for r in rows:
            items.append({
                "id": r[0],
                "id_type": r[1],
                "cle": r[2],
                "categorie": r[3],
                "valeur": r[4],
                "date": r[5],
            })
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
        rows, total = find_configurations_archived_paginated(cur, page, page_size)
        items = []
        for r in rows:
            items.append({
                "id": r[0],
                "id_type": r[1],
                "cle": r[2],
                "categorie": r[3],
                "valeur": r[4],
                "date": r[5],
            })
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
        rows = get_liste_archiver(cur)
        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "id_type": r[1],
                "cle": r[2],
                "categorie": r[3],
                "valeur": r[4],
                "date": r[5],
            })
        return result


def getDetailConfiguration(id_configuration):
    with lecture() as cur:
        if cur is None:
            return None
        row = get_configuration_by_id(cur, id_configuration)
        if row is None:
            return None
        result = []
        result.append({
            "id": row[0],
            "id_type": row[1],
            "cle": row[2],
            "categorie": row[3],
            "valeur": row[4],
            "date": row[5],
        })
        return result


def InsertConfiguration(id_type, valeur):
    with transaction() as cur:
        if cur is None:
            return None
        if not id_type:
            raise ValidationError("Le type de configuration est obligatoire")
        if valeur is None or (isinstance(valeur, str) and not valeur.strip()):
            raise ValidationError("La valeur de la configuration est obligatoire")
        if get_type_configuration_by_id(cur, id_type) is None:
            raise NotFoundError("Le type de configuration est introuvable")
        if verifier_configuration_type_existe(cur, id_type) is not None:
            raise ConflictError("Une configuration pour ce type existe déjà")
        id_configuration = insert_configuration(cur, id_type, valeur)
        if id_configuration is not None:
            insert_configuration_statut(cur, id_configuration, ID_STATUT_CREER)
    cache_invalidate_prefix("configurations:")
    return id_configuration


def UpdateConfiguration(id_configuration, valeur):
    with transaction() as cur:
        if cur is None:
            return False
        if valeur is None or (isinstance(valeur, str) and not valeur.strip()):
            raise ValidationError("La valeur de la configuration est obligatoire")
        existante = get_configuration_by_id(cur, id_configuration)
        if existante is None:
            raise NotFoundError("Configuration introuvable")
        updated_id = update_configuration(cur, id_configuration, valeur)
        if updated_id is not None:
            insert_configuration_statut(cur, updated_id, ID_STATUT_MODIFIER)
    cache_invalidate_prefix("configurations:")
    return True


def deleteConfiguration(id_configuration):
    with transaction() as cur:
        if cur is None:
            return False
        if get_configuration_by_id(cur, id_configuration) is None:
            raise NotFoundError("Configuration introuvable")
        delete_configuration(cur, id_configuration, ID_STATUT_SUPPRIMER)
    cache_invalidate_prefix("configurations:")
    return True


def hardDeleteConfiguration(id_configuration):
    with transaction() as cur:
        if cur is None:
            return False
        supprime = hard_delete_configuration(cur, id_configuration)
        if not supprime:
            raise NotFoundError("Configuration introuvable")
    cache_invalidate_prefix("configurations:")
    return supprime


def reStaurer(id_configuration):
    with transaction() as cur:
        if cur is None:
            return False
        if get_by_id_liste_archiver(cur, id_configuration) is None:
            raise NotFoundError("Configuration introuvable")
        restore_configuration(cur, id_configuration, ID_STATUT_RESTAURER)
    cache_invalidate_prefix("configurations:")
    return id_configuration


def get_liste_type_configuration_by_categorie(id_categorie):
    with lecture() as cur:
        if cur is None:
            return []
        rows = get_type_configuration_by_categorie(cur, id_categorie)
        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "type": r[1],
            })
        return result


def get_liste_categorie_configuration():
    with lecture() as cur:
        if cur is None:
            return []
        rows = get_categorie_configuration(cur)
        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "categorie": r[1],
            })
        return result
