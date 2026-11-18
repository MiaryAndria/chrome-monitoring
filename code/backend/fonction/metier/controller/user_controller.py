from typing import List

from fastapi import APIRouter, HTTPException, Response, Depends, Query
from backend.exceptions import ForbiddenError
from backend.fonction.metier.models.user import (
    UserLogin, UserPasswordUpdate, UserRecentResponse, UserSignin, UserRoleUpdate, UserResponse, UserPageResponse, MeResponse,
)
from backend.fonction.metier.service.user_service import (
    get_utilisateur_recent, login_user, signin_user, get_users, get_role, update_role,
    getUsersPage, getUsersArchivePage, archiver_user, restaurer_user, update_user_password,
)
from backend.core.security import (
    create_access_token, get_current_user, require_admin, set_auth_cookie, COOKIE_NAME,
)

router = APIRouter()


@router.post("/login", response_model=UserResponse)
def login(data: UserLogin, response: Response):
    user = login_user(data.email, data.mdp)

    token = create_access_token(user[0], user[2], user[4])
    set_auth_cookie(response, token)
    return {"id": user[0], "nom": user[1], "email": user[2], "id_role": user[4]}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"message": "Déconnecté"}


@router.post("/signin", response_model=UserResponse)
def signin(data: UserSignin, response: Response):
    user = signin_user(data.nom, data.email, data.mdp, data.confirm_mdp)
    token = create_access_token(user[0], user[2], user[3])
    set_auth_cookie(response, token)
    return {"id": user[0], "nom": user[1], "email": user[2], "id_role": user[3]}


@router.get("/liste")
def liste(current_user: dict = Depends(require_admin)):
    return get_users()


@router.get("/liste/page", response_model=UserPageResponse)
def liste_page(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=10000), current_user: dict = Depends(require_admin)):
    return getUsersPage(page=page, page_size=page_size)


@router.get("/liste/archiver/page", response_model=UserPageResponse)
def liste_archive_page(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=10000), current_user: dict = Depends(require_admin)):
    return getUsersArchivePage(page=page, page_size=page_size)


@router.get("/role")
def roles(current_user: dict = Depends(require_admin)):
    return get_role()


@router.put("/{id}/role", response_model=UserResponse)
def update_role_user(id: int, data: UserRoleUpdate, current_user: dict = Depends(require_admin)):
    return update_role(id, data.id_role)


@router.put("/{id}/update/password")
def update_password_user(id: int, data: UserPasswordUpdate, current_user: dict = Depends(get_current_user)):
    if current_user.get("id") != id and current_user.get("id_role") != 1:
        raise ForbiddenError("Accès refusé")
    update_user_password(id, data.mdp, data.old_pwd, data.confirm_mdp)
    return {"message": "Mot de passe mis à jour"}


@router.post("/{id}/delete")
def supprimer(id: int, current_user: dict = Depends(require_admin)):
    archiver_user(id)
    return {"message": "Utilisateur supprimé"}


@router.get("/recent", response_model=List[UserRecentResponse])
def liste_utilisateur_recent():
    return get_utilisateur_recent()


@router.post("/{id}/restaurer")
def restaurer(id: int, current_user: dict = Depends(require_admin)):
    restaurer_user(id)
    return {"message": "Utilisateur restauré"}


@router.get("/me", response_model=MeResponse)
def me(current_user: dict = Depends(get_current_user)):
    return current_user
