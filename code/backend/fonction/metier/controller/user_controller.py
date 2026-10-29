from fastapi import APIRouter, HTTPException, Response, Depends, Query
from backend.fonction.metier.models.user import (
    UserLogin, UserSignin, UserRoleUpdate, UserResponse, UserPageResponse, MeResponse,
)
from backend.fonction.metier.service.user_service import (
    login_user, signin_user, get_users, get_role, update_role,
    getUsersPage, getUsersArchivePage, archiver_user, restaurer_user,
)
from backend.core.security import (
    create_access_token, get_current_user, require_admin, set_auth_cookie, COOKIE_NAME,
)

router = APIRouter()


@router.post("/login", response_model=UserResponse)
def login(data: UserLogin, response: Response):
    user = login_user(data.email, data.mdp)
    if user is None:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    token = create_access_token(user[0], user[2], user[4])
    set_auth_cookie(response, token)
    return {"id": user[0], "nom": user[1], "email": user[2], "id_role": user[4]}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"message": "Déconnecté"}


@router.post("/signin", response_model=UserResponse)
def signin(data: UserSignin, response: Response):
    try:
        user = signin_user(data.nom, data.email, data.mdp)
    except ValueError as erreur:
        raise HTTPException(status_code=400, detail=str(erreur))

    token = create_access_token(user[0], user[2], user[3])
    set_auth_cookie(response, token)
    return {"id": user[0], "nom": user[1], "email": user[2], "id_role": user[3]}


@router.get("/liste")
def liste(current_user: dict = Depends(require_admin)):
    return get_users()


@router.get("/liste/page", response_model=UserPageResponse)
def liste_page(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), current_user: dict = Depends(require_admin)):
    return getUsersPage(page=page, page_size=page_size)


@router.get("/liste/archiver/page", response_model=UserPageResponse)
def liste_archive_page(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), current_user: dict = Depends(require_admin)):
    return getUsersArchivePage(page=page, page_size=page_size)


@router.get("/role")
def roles(current_user: dict = Depends(require_admin)):
    return get_role()


@router.put("/{id}/role", response_model=UserResponse)
def update_role_user(id: int, data: UserRoleUpdate, current_user: dict = Depends(require_admin)):
    try:
        return update_role(id, data.id_role)
    except ValueError as erreur:
        raise HTTPException(status_code=400, detail=str(erreur))


@router.post("/{id}/delete")
def supprimer(id: int, current_user: dict = Depends(require_admin)):
    try:
        archiver_user(id)
    except ValueError as erreur:
        raise HTTPException(status_code=400, detail=str(erreur))
    return {"message": "Utilisateur supprimé"}


@router.post("/{id}/restaurer")
def restaurer(id: int, current_user: dict = Depends(require_admin)):
    try:
        restaurer_user(id)
    except ValueError as erreur:
        raise HTTPException(status_code=400, detail=str(erreur))
    return {"message": "Utilisateur restauré"}


@router.get("/me", response_model=MeResponse)
def me(current_user: dict = Depends(get_current_user)):
    return current_user
