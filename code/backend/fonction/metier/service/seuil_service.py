from backend.fonction.conn.transaction import lecture, transaction
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
    verifier_seuil_type_existe,
    get_type_seuil_by_categorie,
    get_type_seuil_info,
    get_categorie_seuil,
    update_sens_seuil,
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
        "sens": row[6],
        "limite": row[7],
    }


def _valider_valeur_seuil(valeur, limite):
    """Valide la valeur d'un seuil : entier, >= 0, <= limite du type."""
    try:
        v = int(valeur)
    except (TypeError, ValueError):
        raise ValueError("La valeur du seuil doit être un nombre entier.")

    if v < 0:
        raise ValueError("La valeur du seuil ne peut pas être négative.")

    if limite is not None and v > limite:
        raise ValueError(
            f"La valeur du seuil ne peut pas dépasser {limite} pour ce type de seuil."
        )

    return v


def getListeSeuil():
    with lecture() as cur:
        if cur is None:
            return []
        return [_row_to_dict(r) for r in get_liste_seuil(cur)]


def _fetch_seuils_page(page=1, page_size=10, categorie=None):
    with lecture() as cur:
        if cur is None:
            return build_page([], 0, page, page_size)
        rows = find_seuils_paginated(cur, page, page_size, categorie)
        total = rows[0][8] if rows else 0
        items = [_row_to_dict(r) for r in rows]
        return build_page(items, total, page, page_size)


def getSeuilsPage(page=1, page_size=10, categorie=None):
    cle = f"seuils:{page}:{page_size}:{categorie}"
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    resultat = _fetch_seuils_page(page, page_size, categorie)
    return cache_set(cle, resultat)


def _fetch_seuils_archive_page(page=1, page_size=10):
    with lecture() as cur:
        if cur is None:
            return build_page([], 0, page, page_size)
        rows = find_seuils_archived_paginated(cur, page, page_size)
        total = rows[0][8] if rows else 0
        items = [_row_to_dict(r) for r in rows]
        return build_page(items, total, page, page_size)


def getSeuilsArchivePage(page=1, page_size=10):
    cle = f"seuils:archive:{page}:{page_size}"
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    resultat = _fetch_seuils_archive_page(page, page_size)
    return cache_set(cle, resultat)


def getListeArchiveSeuil():
    with lecture() as cur:
        if cur is None:
            return []
        return [_row_to_dict(r) for r in get_liste_archiver(cur)]


def getDetailSeuil(id_seuil):
    with lecture() as cur:
        if cur is None:
            return None
        row = get_seuil_by_id(cur, id_seuil)
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
            "sens": row[6],
            "limite": row[7], 
        })
        return result 


def InsertSeuil(id_type, valeur):
    with transaction() as cur:
        if cur is None:
            return None
        info = get_type_seuil_info(cur, id_type)
        if info is None:
            raise ValueError("Type de seuil introuvable.")
        valeur = _valider_valeur_seuil(valeur, info[2])

        if verifier_seuil_type_existe(cur, id_type) is not None:
            raise ValueError(
                "Ce seuil existe déjà. Modifiez-le si vous voulez changer la valeur."
            )
        id_seuil = insert_seuil(cur, id_type, valeur)
        if id_seuil is not None:
            insert_seuil_statut(cur, id_seuil, ID_STATUT_CREER)
    cache_invalidate_prefix("seuils:")
    return id_seuil


def UpdateSeuil(id_seuil, valeur, sens=None):
    with transaction() as cur:
        if cur is None:
            return False
        seuil_actuel = get_seuil_by_id(cur, id_seuil)
        if seuil_actuel is None:
            raise ValueError("Seuil introuvable.")

        info = get_type_seuil_info(cur, seuil_actuel[1])
        limite = info[2] if info else None
        valeur = _valider_valeur_seuil(valeur, limite)

        if sens is not None and sens not in (">", "<"):
            raise ValueError("Le sens doit être '>' ou '<'.")

        updated_id = update_seuil(cur, id_seuil, valeur)
        if updated_id is not None:
            insert_seuil_statut(cur, updated_id, ID_STATUT_MODIFIER)
        if sens:
            update_sens_seuil(cur, id_seuil, sens)
    cache_invalidate_prefix("seuils:")
    return True


def deleteSeuil(id_seuil):
    with transaction() as cur:
        if cur is None:
            return False
        delete_seuil(cur, id_seuil, ID_STATUT_SUPPRIMER)
    cache_invalidate_prefix("seuils:")
    return True


def hardDeleteSeuil(id_seuil):
    with transaction() as cur:
        if cur is None:
            return False
        supprime = hard_delete_seuil(cur, id_seuil)
    cache_invalidate_prefix("seuils:")
    return supprime


def reStaurer(id_seuil):
    with transaction() as cur:
        if cur is None:
            return False
        if get_by_id_liste_archiver(cur, id_seuil) is None:
            return False
        restore_seuil(cur, id_seuil, ID_STATUT_RESTAURER)
    cache_invalidate_prefix("seuils:")
    return id_seuil


def get_liste_type_seuil_by_categorie(id_categorie):
    with lecture() as cur:
        if cur is None:
            return []
        rows = get_type_seuil_by_categorie(cur, id_categorie)
        return [
            {
                "id": r[0],
                "type": r[1],
                "limite": r[2],
            }
            for r in rows
        ]


def get_liste_categorie_seuil():
    with lecture() as cur:
        if cur is None:
            return []
        rows = get_categorie_seuil(cur)
        return [
            {
                "id": r[0],
                "categorie": r[1],
            }
            for r in rows
        ]
