from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from backend.fonction.metier.models.device import DeviceResponses, DevicePageResponse
from backend.fonction.metier.service.device_service import (
    getListeDevice,
    getDeviceFiltered,
    getDeviceDetail,
    getDevicesPage,
    get_modeles,
)
from backend.utils.validation import is_valid_datetime_range
import traceback

router = APIRouter()


@router.get("/liste", response_model=DevicePageResponse)
def getListe(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    id_filiale: Optional[int] = None,
    filiale: Optional[str] = None,
    statut: Optional[str] = None,
    type_appareil: Optional[str] = None,
    modele: Optional[str] = None,
    recherche: Optional[str] = None,
    datetime_from: Optional[datetime] = None,
    datetime_to: Optional[datetime] = None,
):
    if not is_valid_datetime_range(datetime_from, datetime_to):
        raise HTTPException(
            status_code=400,
            detail="datetime_to doit être supérieur ou égal à datetime_from",
        )
    try:
        return getDevicesPage(
            page=page,
            page_size=page_size,
            id_filiale=id_filiale,
            filiale=filiale,
            statut=statut,
            type_appareil=type_appareil,
            modele=modele,
            recherche=recherche,
            datetime_from=datetime_from,
            datetime_to=datetime_to,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/modeles", response_model=List[str])
def getModeles():
    try:
        return get_modeles()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=List[DeviceResponses])
def getListeFiltrer(recherche: str = Query(...)):
    try:
        liste = getDeviceFiltered(recherche)
        return liste
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}", response_model=DeviceResponses)
def getDetailDevice(id):
    try:
        device = getDeviceDetail(id)

        if device is None:
            raise HTTPException(
                status_code=404,
                detail="Device introuvable"
            )

        return device

    except HTTPException:
        raise

    except Exception as e:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
