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
    get_type_seuil_by_id,
    get_type_seuil_info,
    get_categorie_seuil,
    update_sens_seuil,
    update_limite_type_seuil,
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

def _unite_seuil(type_seuil: str | None) -> str:
    # Par défaut les seuils sont en pourcentage, sauf quelques métriques en valeur entière.
    if type_seuil in {"seuil_capteur_cpu", "seuil_tache_print", "seuil_evenements"}:
        return "int"
    return "%"


def _valider_limite_type(type_seuil: str | None, limite):
    if limite is None:
        return None
    if not isinstance(limite, int) or isinstance(limite, bool):
        raise ValidationError("La limite du seuil doit être un entier.")
    if limite < 0:
        raise ValidationError("La limite du seuil ne peut pas être négative.")
    max_autorise = 150 if type_seuil == "seuil_capteur_cpu" else 100
    if limite > max_autorise:
        raise ValidationError(
            f"La limite du type de seuil ne peut pas dépasser {max_autorise}."
        )
    return limite


def _valider_valeur_seuil(valeur, limite, type_seuil: str | None = None):
    if valeur is None or (isinstance(valeur, str) and valeur.strip() == ""):
        raise ValidationError("La valeur du seuil est obligatoire.")
    if isinstance(valeur, bool) or not isinstance(valeur, int):
        raise ValidationError("La valeur du seuil doit être un nombre entier.")
    if valeur < 0:
        raise ValidationError("La valeur du seuil ne peut pas être négative.")
    if limite is not None and valeur > limite:
        raise ValidationError(
            f"La valeur du seuil ne peut pas dépasser {limite} pour ce type de seuil."
        )
    return valeur


def getListeSeuil():
    with lecture() as cur:
        if cur is None:
            return []
        rows = get_liste_seuil(cur)
        return [_map_seuil_row(r) for r in rows]


def _map_seuil_row(r):
    return {
        "id": r[0],
        "id_type": r[1],
        "cle": r[2],
        "categorie": r[3],
        "valeur": r[4],
        "date": r[5],
        "sens": r[6],
        "limite": r[7],
        "unite": _unite_seuil(r[2]),
    }


def _fetch_seuils_page(page=1, page_size=10, categorie=None):
    with lecture() as cur:
        if cur is None:
            return build_page([], 0, page, page_size)
        rows, total = find_seuils_paginated(cur, page, page_size, categorie)
        items = [_map_seuil_row(r) for r in rows]
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
        rows, total = find_seuils_archived_paginated(cur, page, page_size)
        items = [_map_seuil_row(r) for r in rows]
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
        rows = get_liste_archiver(cur)
        return [_map_seuil_row(r) for r in rows]


def getDetailSeuil(id_seuil):
    with lecture() as cur:
        if cur is None:
            return None
        row = get_seuil_by_id(cur, id_seuil)
        if row is None:
            return None
        return [_map_seuil_row(row)] 


def InsertSeuil(id_type, valeur):
    with transaction() as cur:
        if cur is None:
            raise ValidationError("Erreur de connexion à la base de données.")
        if id_type is None or (isinstance(id_type, str) and not str(id_type).strip()):
            raise ValidationError("Le type de seuil est manquant.")
        try:
            id_type = int(id_type)
        except (TypeError, ValueError):
            raise ValidationError("Le type de seuil est invalide.")
        info = get_type_seuil_info(cur, id_type)
        if info is None:
            raise NotFoundError("Le type de seuil est introuvable.")
        valeur = _valider_valeur_seuil(valeur, info[2], info[0])

        if verifier_seuil_type_existe(cur, id_type) is not None:
            raise ConflictError("Un seuil pour ce type existe déjà.")
        id_seuil = insert_seuil(cur, id_type, int(valeur))
        if id_seuil is not None:
            insert_seuil_statut(cur, id_seuil, ID_STATUT_CREER)
    cache_invalidate_prefix("seuils:")
    return id_seuil


def UpdateSeuil(id_seuil, valeur, sens=None):
    with transaction() as cur:
        if cur is None:
            raise ValidationError("Erreur de connexion à la base de données.")
        seuil_actuel = get_seuil_by_id(cur, id_seuil)
        if seuil_actuel is None:
            raise NotFoundError("Seuil introuvable.")

        info = get_type_seuil_info(cur, seuil_actuel[1])
        if info is None:
            raise NotFoundError("Le type de seuil est introuvable.")
        valeur = _valider_valeur_seuil(valeur, info[2], info[0])

        if sens is not None and sens not in (">", "<"):
            raise ValidationError("Le sens est invalide : il doit être '>' ou '<'.")

        updated_id = update_seuil(cur, id_seuil, int(valeur))
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
        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "type": r[1],
                "limite": r[2],
                "unite": _unite_seuil(r[1]),
            })
        return result


def update_limite_seuil_type(id_type, limite):
    with transaction() as cur:
        if cur is None:
            raise ValidationError("Erreur de connexion à la base de données")
        type_info = get_type_seuil_by_id(cur, id_type)
        if type_info is None:
            raise NotFoundError("Le type de seuil est introuvable.")

        type_seuil = type_info[1]
        limite_validee = _valider_limite_type(type_seuil, limite)

        # Si une valeur de seuil existe pour ce type, la nouvelle limite doit rester cohérente.
        existant = verifier_seuil_type_existe(cur, id_type)
        if existant is not None and limite_validee is not None and existant[1] is not None:
            if existant[1] > limite_validee:
                raise ValidationError(
                    f"La limite ne peut pas être inférieure à la valeur actuelle du seuil ({existant[1]})."
                )

        updated = update_limite_type_seuil(cur, id_type, limite_validee)
        if updated is None:
            raise NotFoundError("Le type de seuil est introuvable.")

    cache_invalidate_prefix("seuils:")
    return {
        "id": updated[0],
        "type": updated[1],
        "limite": updated[2],
        "unite": _unite_seuil(updated[1]),
    }


def get_liste_categorie_seuil():
    with lecture() as cur:
        if cur is None:
            return []
        rows = get_categorie_seuil(cur)
        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "categorie": r[1],
            })
        return result
