from backend.fonction.conn.transaction import lecture, transaction
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
    with lecture() as cur:
        if cur is None:
            return []
        return [_statut_to_dict(l) for l in get_liste_statut(cur)]


def getListeStatutAll():
    with lecture() as cur:
        if cur is None:
            return []
        return [_statut_to_dict(l) for l in get_liste_statut_all(cur)]


def _fetch_statuts_page(page=1, page_size=10):
    with lecture() as cur:
        if cur is None:
            return build_page([], 0, page, page_size)
        rows = find_statuts_paginated(cur, page, page_size)
        total = rows[0][2] if rows else 0
        items = [_statut_to_dict(r) for r in rows]
        return build_page(items, total, page, page_size)


def getStatutsPage(page=1, page_size=10):
    cle = f"statuts:{page}:{page_size}"
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    return cache_set(cle, _fetch_statuts_page(page, page_size))


def getDetailStatut(id_statut):
    with lecture() as cur:
        if cur is None:
            return None
        row = get_statut_by_id(cur, id_statut)
        if row is None:
            return None
        return _statut_to_dict(row)


def UpdateStatut(id_statut, nom):
    nom = (nom or "").strip()
    if not nom:
        raise ValueError("Le nom du statut est obligatoire")

    try:
        with transaction() as cur:
            if cur is None:
                raise ValueError("Erreur de connexion à la base de données")
            existant = get_statut_by_name(cur, nom)
            if existant is not None and existant[0] != id_statut:
                raise ValueError("Ce nom de statut existe déjà")

            updated_id = update_statut(cur, id_statut, nom)
            if updated_id is None:
                raise ValueError("Statut introuvable")
    except ValueError:
        raise
    except Exception:
        raise ValueError("Impossible de mettre à jour le statut")

    cache_invalidate_prefix("statuts:")
    cache_invalidate_prefix("devices:")
    cache_invalidate_prefix("dashboard:")
    return True


# if __name__ == "__main__":
#     getListeStatut()
