from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Query

from backend.exceptions import ValidationError
from backend.fonction.metier.models.filiale import (
    FilialeResponse,
    FilialePageResponse,
)
from backend.fonction.metier.models.device import DevicePageResponse
from backend.fonction.metier.service.filiale_service import (
    get_all_filiales,
    get_devices_by_filiale,
    get_filiales_page,
    get_filiale_stats,
)
from backend.utils.validation import is_valid_datetime_range

router = APIRouter()


@router.get("/liste", response_model=List[FilialeResponse])
def getListeFiliale():
    filiales = get_all_filiales()
    if filiales is None:
        raise ValidationError("Impossible de récupérer la liste des filiales")
    result = []
    for f in filiales:
        result.append({
            "id": f[0],
            "org_unit_path": f[1],
        })
    return result


@router.get("/liste/page", response_model=FilialePageResponse)
def getFilialesPage(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    recherche: Optional[str] = None,
):
    return get_filiales_page(page=page, page_size=page_size, recherche=recherche)


@router.get("/{id_filiale}/stats")
def getFilialeStats(id_filiale: int):
    return get_filiale_stats(id_filiale)


@router.get("/{id_filiale}/devices", response_model=DevicePageResponse)
def getDevicesByFiliale(
    id_filiale: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    id_statut: Optional[int] = None,
    statut: Optional[str] = None,
    type_appareil: Optional[str] = None,
    modele: Optional[str] = None,
    recherche: Optional[str] = None,
    utilisateur_recent: Optional[str] = None,
    datetime_from: Optional[datetime] = None,
    datetime_to: Optional[datetime] = None,
):
    if not is_valid_datetime_range(datetime_from, datetime_to):
        raise ValidationError("datetime_to doit être supérieur ou égal à datetime_from")
    return get_devices_by_filiale(
        id_filiale,
        page=page,
        page_size=page_size,
        id_statut=id_statut,
        statut=statut,
        type_appareil=type_appareil,
        modele=modele,
        recherche=recherche,
        utilisateur_recent=utilisateur_recent,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
    )
