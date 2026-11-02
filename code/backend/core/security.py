import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from jose import JWTError, jwt
from fastapi import Request, Response, HTTPException, status, Depends

from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.user import get_role_by_user_id

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY manquante dans le fichier .env")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
COOKIE_NAME = "access_token"
RENEW_THRESHOLD = timedelta(days=3)
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"

ID_ROLE_ADMIN = 1
ID_ROLE_LECTURE = 2


def create_access_token(user_id: int, email: str, id_role: Optional[int] = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": id_role,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def set_auth_cookie(response: Response, token: str):
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )


def _role_depuis_base(user_id):
    connexion = get_connection()
    if connexion is None:
        return None
    try:
        cur = connexion.cursor()
        return get_role_by_user_id(cur, user_id)
    finally:
        close_connection(connexion)


async def get_current_user(request: Request, response: Response) -> dict:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]

    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Non authentifié")

    payload = decode_token(token)
    if not payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session expirée")

    # Le role est relu en base : un changement de role est effectif au prochain appel,
    # sans dependre du contenu du token (et sans re-login).
    user_id = int(payload["sub"])
    id_role = _role_depuis_base(user_id)
    if id_role is None:
        id_role = payload.get("role")

    # Renouvellement glissant : nouveau token si l'ancien approche de sa fin
    expire_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    if expire_at - datetime.now(timezone.utc) < RENEW_THRESHOLD:
        new_token = create_access_token(user_id, payload["email"], id_role)
        set_auth_cookie(response, new_token)

    return {"id": user_id, "email": payload["email"], "id_role": id_role}


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("id_role") != ID_ROLE_ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Accès réservé aux administrateurs")
    return current_user