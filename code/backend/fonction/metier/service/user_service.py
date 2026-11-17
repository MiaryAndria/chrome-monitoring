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
    get_liste_utilisateur_recent,
    get_user_auth_by_id,
    update_user_mdp,
)
from backend.fonction.metier.repository.statut import (
    ID_STATUT_CREER,
    ID_STATUT_SUPPRIMER,
    ID_STATUT_RESTAURER,
    ID_STATUT_MODIFIER,
)
from backend.utils.password_hashage import verifier_password, hasher_password
from backend.utils.pagination import build_page
from backend.core.cache import cache_get, cache_set
from backend.exceptions import ValidationError, NotFoundError, ConflictError, ForbiddenError, UnauthorizedError
import re

UTILISATEURS_RECENTS_CACHE_KEY = "users:recent:all"
UTILISATEURS_RECENTS_CACHE_TTL = 60

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ID_ROLE_LECTURE = 2

def login_user(email, mdp):
    email = (email or "").strip()
    mdp = mdp or ""

    if not email and not mdp:
        raise ValidationError("L'email est manquant. Le mot de passe est manquant.")
    if not email:
        raise ValidationError("L'email est manquant.")
    if not mdp:
        raise ValidationError("Le mot de passe est manquant.")

    with lecture() as cur:
        if cur is None:
            raise ValidationError("Erreur de connexion à la base de données")
        user = get_user_by_email(cur, email)

        if user is None:
            raise NotFoundError("Email introuvable.")

        mot_de_passe_hache = user[3]
        if not verifier_password(mdp, mot_de_passe_hache):
            raise UnauthorizedError("Mot de passe incorrect.")

        archive = get_user_archived(cur, user[0], ID_STATUT_SUPPRIMER)

        if archive is not None:
            raise ForbiddenError("Ce compte a été supprimé.")

        return user

def signin_user(nom, email, mdp, confirm_mdp=""):
    nom = (nom or "").strip()
    email = (email or "").strip()
    mdp = mdp or ""
    confirm_mdp = confirm_mdp or ""

    champs_manquants = []
    if not nom:
        champs_manquants.append("nom")
    if not email:
        champs_manquants.append("email")
    if not mdp:
        champs_manquants.append("mot de passe")

    if champs_manquants:
        if len(champs_manquants) == 1:
            raise ValidationError(f"Le champ {champs_manquants[0]} est manquant.")
        raise ValidationError("Les champs suivants sont manquants : " + ", ".join(champs_manquants) + ".")

    if not EMAIL_RE.match(email):
        raise ValidationError("L'email est invalide.")
    if len(mdp) < 6:
        raise ValidationError("Le mot de passe est invalide : il doit contenir au moins 6 caractères.")
    if mdp != confirm_mdp:
        raise ValidationError("La confirmation du mot de passe ne correspond pas.")

    with transaction() as cur:
        if cur is None:
            raise ValidationError("Erreur de connexion à la base de données")
        if get_user_by_email(cur, email) is not None:
            raise ConflictError("Cet email est déjà utilisé.")

        mdp_hache = hasher_password(mdp)
        user = create_user(cur, nom, email, mdp_hache, ID_ROLE_LECTURE)
        if user is not None:
            insert_user_statut(cur, user[0], ID_STATUT_CREER)
        return user

def get_users():
    with lecture() as cur:
        if cur is None:
            return []
        rows = list_users(cur)
        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "nom": r[1],
                "email": r[2],
                "id_role": r[3],
                "role": r[4],
            })
        return result

def get_utilisateur_recent ():
    valeur = cache_get(UTILISATEURS_RECENTS_CACHE_KEY)
    if valeur is not None:
        return valeur

    with lecture() as cur:
        if cur is None:
            return []
        rows = get_liste_utilisateur_recent(cur)
        items = []
        for r in rows:
            items.append({"id": r[0], "email": r[1]})
        return cache_set(
            UTILISATEURS_RECENTS_CACHE_KEY,
            items,
            UTILISATEURS_RECENTS_CACHE_TTL,
        )

def get_role():
    with lecture() as cur:
        if cur is None:
            return []
        rows = get_roles_repo(cur)
        result = []
        for r in rows:
            result.append({"id": r[0], "role": r[1]})
        return result


def update_role(id_user, id_role):
    with transaction() as cur:
        if cur is None:
            raise ValidationError("Erreur de connexion à la base de données")
        if not role_exists(cur, id_role):
            raise NotFoundError("Le rôle référencé n'existe pas")

        user = set_user_role(cur, id_user, id_role)
        if user is None:
            raise NotFoundError("Utilisateur introuvable")

        insert_user_statut(cur, user[0], ID_STATUT_MODIFIER)
        return {"id": user[0], "nom": user[1], "email": user[2], "id_role": user[3]}


def getUsersPage(page=1, page_size=10):
    with lecture() as cur:
        if cur is None:
            return build_page([], 0, page, page_size)
        rows, total = find_users_paginated(cur, ID_STATUT_SUPPRIMER, page, page_size)
        items = []
        for r in rows:
            items.append({
                "id": r[0],
                "nom": r[1],
                "email": r[2],
                "id_role": r[3],
                "role": r[4],
                "date": r[5],
            })
        return build_page(items, total, page, page_size)


def getUsersArchivePage(page=1, page_size=10):
    with lecture() as cur:
        if cur is None:
            return build_page([], 0, page, page_size)
        rows, total = find_users_archived_paginated(cur, ID_STATUT_SUPPRIMER, page, page_size)
        items = []
        for r in rows:
            items.append({
                "id": r[0],
                "nom": r[1],
                "email": r[2],
                "id_role": r[3],
                "role": r[4],
                "date": r[5],
            })
        return build_page(items, total, page, page_size)


def archiver_user(id_user):
    with transaction() as cur:
        if cur is None:
            raise ValidationError("Erreur de connexion à la base de données")
        if get_user_by_id(cur, id_user) is None:
            raise NotFoundError("Utilisateur introuvable")

        insert_user_statut(cur, id_user, ID_STATUT_SUPPRIMER)
        return True

def update_user_password(id_user, new_pwd, old_pwd):
    new_pwd = new_pwd or ""
    old_pwd = old_pwd or ""

    champs_manquants = []
    if not old_pwd.strip():
        champs_manquants.append("ancien mot de passe")
    if not new_pwd.strip():
        champs_manquants.append("nouveau mot de passe")

    if champs_manquants:
        if len(champs_manquants) == 1:
            raise ValidationError(f"Le champ {champs_manquants[0]} est manquant.")
        raise ValidationError("Les champs suivants sont manquants : " + ", ".join(champs_manquants) + ".")

    if len(new_pwd) < 6:
        raise ValidationError("Le nouveau mot de passe doit contenir au moins 6 caractères.")

    with transaction() as cur:
        if cur is None:
            raise ValidationError("Erreur de connexion à la base de données")

        user = get_user_auth_by_id(cur, id_user)
        if user is None:
            raise NotFoundError("Utilisateur introuvable")

        if not verifier_password(old_pwd, user[3]):
            raise ValidationError("L'ancien mot de passe est incorrect.")

        mdp_hache = hasher_password(new_pwd)
        update_user_mdp(cur, id_user, mdp_hache)
        insert_user_statut(cur, id_user, ID_STATUT_MODIFIER)

    return True


def restaurer_user(id_user):
    with transaction() as cur:
        if cur is None:
            raise ValidationError("Erreur de connexion à la base de données")
        if get_user_archived(cur, id_user, ID_STATUT_SUPPRIMER) is None:
            raise NotFoundError("Utilisateur introuvable")

        insert_user_statut(cur, id_user, ID_STATUT_RESTAURER)
        return True
