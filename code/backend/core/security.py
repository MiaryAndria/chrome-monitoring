import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from jose import JWTError, jwt
from fastapi import Request, Response, HTTPException, status

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY manquante dans le fichier .env")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
COOKIE_NAME = "access_token"
RENEW_THRESHOLD = timedelta(days=3)
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"


def create_access_token(user_id: int, email: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
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

    # Renouvellement glissant : nouveau token si l'ancien approche de sa fin
    expire_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    if expire_at - datetime.now(timezone.utc) < RENEW_THRESHOLD:
        new_token = create_access_token(int(payload["sub"]), payload["email"])
        set_auth_cookie(response, new_token)

    return {"id": int(payload["sub"]), "email": payload["email"]}