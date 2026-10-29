from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.user import (
    get_user_by_email,
    create_user,
    get_role as get_roles_repo,
    list_users,
    role_exists,
    set_user_role,
    get_user_by_id,
    get_user_archived,
    find_users_paginated,
    find_users_archived_paginated,
    insert_user_statut,
)
from backend.fonction.metier.repository.statut import get_or_create_statut
from backend.utils.password_hashage import verifier_password, hasher_password
from backend.utils.pagination import build_page

ID_ROLE_LECTURE = 2

# Noms de statuts (t_statut.nom) : les ids sont résolus en base, jamais codés en dur
NOM_STATUT_CREER = "CREER"
NOM_STATUT_SUPPRIMER = "SUPPRIMER"
NOM_STATUT_RESTAURER = "RESTAURER"
NOM_STATUT_MODIFIER="MODIFIER"


def _id_statut(cur, nom):
    return get_or_create_statut(cur, nom)


def _user_to_dict(row):
    return {
        "id": row[0],
        "nom": row[1],
        "email": row[2],
        "id_role": row[3],
        "role": row[4],
        "date": row[5],
    }


def login_user(email, mdp):
    if not email or not mdp:
        return None

    connexion = get_connection()
    if connexion is None:
        return None

    try:
        cur = connexion.cursor()
        user = get_user_by_email(cur, email)

        if user is None:
            cur.close()
            return None

        mot_de_passe_hache = user[3]
        if not verifier_password(mdp, mot_de_passe_hache):
            cur.close()
            return None

        id_statut_supprime = _id_statut(cur, NOM_STATUT_SUPPRIMER)
        archive = get_user_archived(cur, user[0], id_statut_supprime)
        cur.close()

        if archive is not None:
            raise ValueError("Ce compte a été supprimé")

        return user
    finally:
        close_connection(connexion)


def signin_user(nom, email, mdp):
    nom = (nom or "").strip()
    email = (email or "").strip()
    mdp = mdp or ""

    if not nom or not email or not mdp:
        raise ValueError("Tous les champs sont obligatoires")
    if len(mdp) < 6:
        raise ValueError("Le mot de passe doit contenir au moins 6 caractères")

    connexion = get_connection()
    if connexion is None:
        raise ValueError("Erreur de connexion à la base de données")

    try:
        cur = connexion.cursor()
        if get_user_by_email(cur, email) is not None:
            cur.close()
            raise ValueError("Cet email est déjà utilisé")

        mdp_hache = hasher_password(mdp)
        user = create_user(cur, nom, email, mdp_hache, ID_ROLE_LECTURE)
        if user is not None:
            insert_user_statut(cur, user[0], _id_statut(cur, NOM_STATUT_CREER))
        connexion.commit()
        cur.close()
        return user
    except ValueError:
        connexion.rollback()
        raise
    except Exception:
        connexion.rollback()
        raise ValueError("Impossible de créer le compte")
    finally:
        close_connection(connexion)


def get_users():
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = list_users(cur)
        cur.close()
        return [
            {"id": r[0], "nom": r[1], "email": r[2], "id_role": r[3], "role": r[4]}
            for r in rows
        ]
    finally:
        close_connection(connexion)


def get_role():
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_roles_repo(cur)
        cur.close()
        return [{"id": r[0], "role": r[1]} for r in rows]
    finally:
        close_connection(connexion)


def update_role(id_user, id_role):
    connexion = get_connection()
    if connexion is None:
        raise ValueError("Erreur de connexion à la base de données")

    try:
        cur = connexion.cursor()
        if not role_exists(cur, id_role):
            cur.close()
            raise ValueError("Rôle inconnu")

        user = set_user_role(cur, id_user, id_role)
        if user is None:
            cur.close()
            raise ValueError("Utilisateur introuvable")

        insert_user_statut(cur, user[0], _id_statut(cur, NOM_STATUT_MODIFIER))
        connexion.commit()
        cur.close()
        return {"id": user[0], "nom": user[1], "email": user[2], "id_role": user[3]}
    except ValueError:
        connexion.rollback()
        raise
    except Exception:
        connexion.rollback()
        raise ValueError("Impossible de mettre à jour le rôle")
    finally:
        close_connection(connexion)


def getUsersPage(page=1, page_size=10):
    connexion = get_connection()
    if connexion is None:
        return build_page([], 0, page, page_size)
    try:
        cur = connexion.cursor()
        id_statut_supprime = _id_statut(cur, NOM_STATUT_SUPPRIMER)
        rows = find_users_paginated(cur, id_statut_supprime, page, page_size)
        total = rows[0][6] if rows else 0
        items = [_user_to_dict(r) for r in rows]
        cur.close()
        return build_page(items, total, page, page_size)
    finally:
        close_connection(connexion)


def getUsersArchivePage(page=1, page_size=10):
    connexion = get_connection()
    if connexion is None:
        return build_page([], 0, page, page_size)
    try:
        cur = connexion.cursor()
        id_statut_supprime = _id_statut(cur, NOM_STATUT_SUPPRIMER)
        rows = find_users_archived_paginated(cur, id_statut_supprime, page, page_size)
        total = rows[0][6] if rows else 0
        items = [_user_to_dict(r) for r in rows]
        cur.close()
        return build_page(items, total, page, page_size)
    finally:
        close_connection(connexion)


def archiver_user(id_user):
    connexion = get_connection()
    if connexion is None:
        raise ValueError("Erreur de connexion à la base de données")

    try:
        cur = connexion.cursor()
        if get_user_by_id(cur, id_user) is None:
            cur.close()
            raise ValueError("Utilisateur introuvable")

        id_statut = _id_statut(cur, NOM_STATUT_SUPPRIMER)
        insert_user_statut(cur, id_user, id_statut)
        connexion.commit()
        cur.close()
        return True
    except ValueError:
        connexion.rollback()
        raise
    except Exception:
        connexion.rollback()
        raise ValueError("Impossible de supprimer l'utilisateur")
    finally:
        close_connection(connexion)


def restaurer_user(id_user):
    connexion = get_connection()
    if connexion is None:
        raise ValueError("Erreur de connexion à la base de données")

    try:
        cur = connexion.cursor()
        id_statut_supprime = _id_statut(cur, NOM_STATUT_SUPPRIMER)
        if get_user_archived(cur, id_user, id_statut_supprime) is None:
            cur.close()
            raise ValueError("Utilisateur introuvable")

        id_statut = _id_statut(cur, NOM_STATUT_RESTAURER)
        insert_user_statut(cur, id_user, id_statut)
        connexion.commit()
        cur.close()
        return True
    except ValueError:
        connexion.rollback()
        raise
    except Exception:
        connexion.rollback()
        raise ValueError("Impossible de restaurer l'utilisateur")
    finally:
        close_connection(connexion)
