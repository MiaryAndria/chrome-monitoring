from fastapi import APIRouter, HTTPException, Response, Depends
from backend.fonction.metier.models.user import UserResponse, UserLogin
from backend.fonction.metier.service.user_service import login_user
from backend.core.security import (
    create_access_token, get_current_user, set_auth_cookie, COOKIE_NAME,
)

router = APIRouter()


@router.post("/login", response_model=UserResponse)
def login(data: UserLogin, response: Response):
    user = login_user(data.email, data.mdp)
    if user is None:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    token = create_access_token(user[0], user[2])
    set_auth_cookie(response, token)
    return {"id": user[0], "nom": user[1], "email": user[2]}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"message": "Déconnecté"}


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return current_user