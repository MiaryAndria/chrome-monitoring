import traceback
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from backend.fonction.metier.models.filiale import (
    FilialeResponse,
    FilialePageResponse,
)
from backend.fonction.metier.models.device import DevicePageResponse
from backend.fonction.metier.service.filiale_service import (
    get_all_filiales,
    get_devices_by_filiale,
    get_filiales_page,
)
from backend.utils.validation import is_valid_datetime_range

router = APIRouter()


@router.get("/liste", response_model=List[FilialeResponse])
def getListeFiliale():
    filiales = get_all_filiales()
    if filiales is None:
        raise HTTPException(
            status_code=500,
            detail="Impossible de récupérer la liste des filiales"
        )
    return [
        {
            "id": f[0],
            "org_unit_path": f[1],
        }
        for f in filiales
    ]


@router.get("/liste/page", response_model=FilialePageResponse)
def getFilialesPage(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    recherche: Optional[str] = None,
):
    try:
        return get_filiales_page(page=page, page_size=page_size, recherche=recherche)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id_filiale}/devices", response_model=DevicePageResponse)
def getDevicesByFiliale(
    id_filiale: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    statut: Optional[str] = None,
    datetime_from: Optional[datetime] = None,
    datetime_to: Optional[datetime] = None,
):
    if not is_valid_datetime_range(datetime_from, datetime_to):
        raise HTTPException(
            status_code=400,
            detail="datetime_to doit être supérieur ou égal à datetime_from",
        )
    try:
        return get_devices_by_filiale(
            id_filiale,
            page=page,
            page_size=page_size,
            statut=statut,
            datetime_from=datetime_from,
            datetime_to=datetime_to,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
