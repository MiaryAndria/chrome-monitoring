from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from backend.fonction.metier.service.alerte_service import (
    getNombreAlerte,
    getDernieresAlertes,
    getListeDeviceAlerteDate,
    getDeviceAlertesPage,
)
from backend.fonction.metier.models.alerte import (
    AlerteNombreResponse,
    AlerteResume,
    AlerteResumePageResponse,
)

router = APIRouter()


@router.get("/nombre", response_model=AlerteNombreResponse)
def nombre_alerte():
    try:
        return {"nombre": getNombreAlerte()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tenAlerte", response_model=List[AlerteResume])
def dix_alertes(limit: int = Query(10, ge=1, le=50)):
    try:
        return getDernieresAlertes(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device", response_model=List[AlerteResume])
def liste_device_alerte(date_debut: Optional[datetime] = None, date_fin: Optional[datetime] = None):
    try:
        return getListeDeviceAlerteDate(date_debut, date_fin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/page", response_model=AlerteResumePageResponse)
def liste_device_alerte_page(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    date_debut: Optional[datetime] = None,
    date_fin: Optional[datetime] = None,
):
    try:
        return getDeviceAlertesPage(page=page, page_size=page_size,
                                    date_debut=date_debut, date_fin=date_fin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
