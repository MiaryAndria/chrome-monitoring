from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Query

from backend.exceptions import NotFoundError
from backend.fonction.metier.models.device import DeviceResponses, DevicePageResponse
from backend.fonction.metier.service.device_service import (
    getDeviceDetail,
    getDevicesPage,
    get_modeles,
    get_device_stats,
)
from backend.utils.validation import valider_plage_datetime

router = APIRouter()


@router.get("/liste", response_model=DevicePageResponse)
def getListe(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=10000),
    id_filiale: Optional[int] = None,
    filiale: Optional[str] = None,
    id_statut: Optional[int] = None,
    statut: Optional[str] = None,
    type_appareil: Optional[str] = None,
    modele: Optional[str] = None,
    recherche: Optional[str] = None,
    datetime_from: Optional[datetime] = None,
    datetime_to: Optional[datetime] = None,
    utilisateur_recent: Optional[str] = None,
):
    valider_plage_datetime(datetime_from, datetime_to)
    return getDevicesPage(
        page=page,
        page_size=page_size,
        id_filiale=id_filiale,
        filiale=filiale,
        id_statut=id_statut,
        statut=statut,
        type_appareil=type_appareil,
        modele=modele,
        recherche=recherche,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
        utilisateur_recent=utilisateur_recent,
    )


@router.get("/modeles", response_model=List[str])
def getModeles():
    return get_modeles()


@router.get("/stats")
def getStats():
    return get_device_stats()


@router.get("/{id}", response_model=DeviceResponses)
def getDetailDevice(id: int):
    device = getDeviceDetail(id)
    if device is None:
        raise NotFoundError("Device introuvable")
    return device
