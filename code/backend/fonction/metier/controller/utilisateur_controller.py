from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from backend.fonction.metier.service.utilisateur_service import (
    get_utilisateurs_recent_page,
    get_utilisateur_recent_devices,
)

router = APIRouter()


@router.get("/recent/page")
def liste_utilisateurs_recent_page(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    filiale: Optional[str] = None,
    recherche: Optional[str] = None,
):
    try:
        return get_utilisateurs_recent_page(
            page=page,
            page_size=page_size,
            filiale=filiale,
            recherche=recherche,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent/{id_utilisateur}/devices")
def liste_devices_utilisateur(
    id_utilisateur: int,
    limit: int = Query(100, ge=1, le=500),
):
    try:
        return get_utilisateur_recent_devices(id_utilisateur, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
