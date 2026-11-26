from backend.fonction.conn.transaction import lecture, transaction
from backend.fonction.metier.repository.synchronisation import (
    get_liste_synchronisation,
    count_synchronisation,
    get_synchronisation_by_id,
    get_synchronisation_en_cours,
    get_statuts_synchronisation,
    delete_synchronisation_statut,
    delete_synchronisation_historique,
)
from backend.core.cache import cache_get, cache_set, cache_invalidate_prefix
from backend.utils.pagination import build_page


def _duree(date_debut, date_fin):
    if date_debut is None or date_fin is None:
        return None
    return round((date_fin - date_debut).total_seconds(), 3)


def getListeSynchronisation(page=1, page_size=10, statut=None, date_debut=None, date_fin=None,fenetre_debut=None,fenetre_fin=None):
    cle = f"synchronisations:liste:{page}:{page_size}:{statut}:{date_debut}:{date_fin}:{fenetre_debut}:{fenetre_fin}"
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur
    with lecture() as cur:
        if cur is None:
            return build_page([], 0, page, page_size)
        offset = (page - 1) * page_size
        rows = get_liste_synchronisation(cur, page_size, offset, statut, date_debut, date_fin,fenetre_debut,fenetre_fin)
        total = count_synchronisation(cur, statut, date_debut, date_fin,fenetre_debut,fenetre_fin)
        items = []
        for r in rows:
            items.append({
                "id": r[0],
                "source": r[1],
                "date_debut": r[2],
                "date_fin": r[3],
                "fenetre_debut": r[4],
                "fenetre_fin": r[5],
                "nb_lignes": r[6] or 0,
                "message": r[7],
                "statut": r[9],
                "date_statut": r[10],
                "duree_s": _duree(r[2], r[3]),
            })
        return cache_set(cle, build_page(items, total, page, page_size))


def getDetailSynchronisation(id_sync):
    with lecture() as cur:
        if cur is None:
            return None
        r = get_synchronisation_by_id(cur, id_sync)
        if r is None:
            return None
        return {
            "id": r[0],
            "source": r[1],
            "date_debut": r[2],
            "date_fin": r[3],
            "fenetre_debut": r[4],
            "fenetre_fin": r[5],
            "nb_lignes": r[6] or 0,
            "message": r[7],
            "statut": r[9],
            "date_statut": r[10],
            "duree_s": _duree(r[2], r[3]),
            "journal": r[8],
        }


def delete_synchronisation(date_limite):
    with transaction() as cur:
        if cur is None:
            return 0
        delete_synchronisation_statut(cur, date_limite)
        delete_synchronisation_historique(cur, date_limite)
    cache_invalidate_prefix("synchronisations:")
    return True


def getSynchronisationEnCours():
    with lecture() as cur:
        if cur is None:
            return None
        r = get_synchronisation_en_cours(cur)
        if r is None:
            return None
        return {
            "id": r[0],
            "source": r[1],
            "date_debut": r[2],
            "date_fin": r[3],
            "fenetre_debut": r[4],
            "fenetre_fin": r[5],
            "nb_lignes": r[6] or 0,
            "message": r[7],
            "statut": r[9],
            "date_statut": r[10],
            "duree_s": _duree(r[2], r[3]),
            "journal": r[8],
        }


def getStatutsSynchronisation():
    with lecture() as cur:
        if cur is None:
            return []
        return [r[0] for r in get_statuts_synchronisation(cur)]
