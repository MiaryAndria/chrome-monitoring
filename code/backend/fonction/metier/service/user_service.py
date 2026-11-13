from backend.fonction.conn.transaction import lecture, transaction
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
    get_liste_utilisateur_recent
)
from backend.fonction.metier.repository.statut.constants import (
    ID_STATUT_CREER,
    ID_STATUT_SUPPRIMER,
    ID_STATUT_RESTAURER,
    ID_STATUT_MODIFIER,
)
from backend.utils.password_hashage import verifier_password, hasher_password
from backend.utils.pagination import build_page
from backend.core.cache import cache_get, cache_set

ID_ROLE_LECTURE = 2

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

    with lecture() as cur:
        if cur is None:
            return None
        user = get_user_by_email(cur, email)

        if user is None:
            return None

        mot_de_passe_hache = user[3]
        if not verifier_password(mdp, mot_de_passe_hache):
            return None

        archive = get_user_archived(cur, user[0], ID_STATUT_SUPPRIMER)

        if archive is not None:
            raise ValueError("Ce compte a été supprimé")

        return user

def signin_user(nom, email, mdp):
    nom = (nom or "").strip()
    email = (email or "").strip()
    mdp = mdp or ""

    if not nom or not email or not mdp:
        raise ValueError("Tous les champs sont obligatoires")
    if len(mdp) < 6:
        raise ValueError("Le mot de passe doit contenir au moins 6 caractères")

    try:
        with transaction() as cur:
            if cur is None:
                raise ValueError("Erreur de connexion à la base de données")
            if get_user_by_email(cur, email) is not None:
                raise ValueError("Cet email est déjà utilisé")

            mdp_hache = hasher_password(mdp)
            user = create_user(cur, nom, email, mdp_hache, ID_ROLE_LECTURE)
            if user is not None:
                insert_user_statut(cur, user[0], ID_STATUT_CREER)
            return user
    except ValueError:
        raise
    except Exception:
        raise ValueError("Impossible de créer le compte")

def get_users():
    with lecture() as cur:
        if cur is None:
            return []
        rows = list_users(cur)
        return [
            {"id": r[0], "nom": r[1], "email": r[2], "id_role": r[3], "role": r[4]}
            for r in rows
        ]

UTILISATEURS_RECENTS_CACHE_KEY = "users:recent:all"
UTILISATEURS_RECENTS_CACHE_TTL = 60


def get_utilisateur_recent ():
    valeur = cache_get(UTILISATEURS_RECENTS_CACHE_KEY)
    if valeur is not None:
        return valeur

    with lecture() as cur:
        if cur is None:
            return []
        rows = get_liste_utilisateur_recent(cur)
        return cache_set(
            UTILISATEURS_RECENTS_CACHE_KEY,
            [{"id": r[0], "email": r[1]} for r in rows],
            UTILISATEURS_RECENTS_CACHE_TTL,
        )

def get_role():
    with lecture() as cur:
        if cur is None:
            return []
        rows = get_roles_repo(cur)
        return [{"id": r[0], "role": r[1]} for r in rows]


def update_role(id_user, id_role):
    try:
        with transaction() as cur:
            if cur is None:
                raise ValueError("Erreur de connexion à la base de données")
            if not role_exists(cur, id_role):
                raise ValueError("Rôle inconnu")

            user = set_user_role(cur, id_user, id_role)
            if user is None:
                raise ValueError("Utilisateur introuvable")

            insert_user_statut(cur, user[0], ID_STATUT_MODIFIER)
            return {"id": user[0], "nom": user[1], "email": user[2], "id_role": user[3]}
    except ValueError:
        raise
    except Exception:
        raise ValueError("Impossible de mettre à jour le rôle")


def getUsersPage(page=1, page_size=10):
    with lecture() as cur:
        if cur is None:
            return build_page([], 0, page, page_size)
        rows = find_users_paginated(cur, ID_STATUT_SUPPRIMER, page, page_size)
        total = rows[0][6] if rows else 0
        items = [_user_to_dict(r) for r in rows]
        return build_page(items, total, page, page_size)


def getUsersArchivePage(page=1, page_size=10):
    with lecture() as cur:
        if cur is None:
            return build_page([], 0, page, page_size)
        rows = find_users_archived_paginated(cur, ID_STATUT_SUPPRIMER, page, page_size)
        total = rows[0][6] if rows else 0
        items = [_user_to_dict(r) for r in rows]
        return build_page(items, total, page, page_size)


def archiver_user(id_user):
    try:
        with transaction() as cur:
            if cur is None:
                raise ValueError("Erreur de connexion à la base de données")
            if get_user_by_id(cur, id_user) is None:
                raise ValueError("Utilisateur introuvable")

            insert_user_statut(cur, id_user, ID_STATUT_SUPPRIMER)
            return True
    except ValueError:
        raise
    except Exception:
        raise ValueError("Impossible de supprimer l'utilisateur")


def restaurer_user(id_user):
    try:
        with transaction() as cur:
            if cur is None:
                raise ValueError("Erreur de connexion à la base de données")
            if get_user_archived(cur, id_user, ID_STATUT_SUPPRIMER) is None:
                raise ValueError("Utilisateur introuvable")

            insert_user_statut(cur, id_user, ID_STATUT_RESTAURER)
            return True
    except ValueError:
        raise
    except Exception:
        raise ValueError("Impossible de restaurer l'utilisateur")
