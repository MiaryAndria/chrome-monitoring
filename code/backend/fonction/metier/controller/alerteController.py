import traceback
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from backend.fonction.metier.service.alerte_service import (
    getListeDeviceAlerteDateResolue,
    getNombreAlerte,
    getDernieresAlertes,
    getListeDeviceAlerteDate,
    getDeviceAlertesPage,
    getDeviceAlertesResoluesPage,
    getNombreAlerteNouvelle,
    getNombreAlerteResolue,
    getNombreAlerteParType,
    getNouvellesAlertes,
    getTypeAlerte,
)
from backend.fonction.metier.models.alerte import (
    AlerteNombreResponse,
    AlerteResponse,
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
    
@router.get("/liste/type",response_model=List[AlerteResponse])
def get_type():
    try:
        listeTypeAlerte = getTypeAlerte()
        return listeTypeAlerte
    except Exception as e:
        traceback.print_exc
        raise HTTPException(status_code=500,detail=str(e))
    
@router.get("/nombre/resolue",response_model=AlerteNombreResponse)
def nombre_alerte_resolue():
    try:
        return {"nombre":getNombreAlerteResolue()}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    

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
    

@router.get("/device/resolue", response_model=List[AlerteResume])
def liste_device_alerte(date_debut: Optional[datetime] = None, date_fin: Optional[datetime] = None):
    try:
        return getListeDeviceAlerteDateResolue(date_debut, date_fin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/resolue/page", response_model=AlerteResumePageResponse)
def liste_device_alerte_resolue_page(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    type:Optional[str]=None,
    search:Optional[str]=None,
    date_debut: Optional[datetime] = None,
    date_fin: Optional[datetime] = None,
):
    try:
        return getDeviceAlertesResoluesPage(page=page, page_size=page_size,
                                            date_debut=date_debut, date_fin=date_fin,type=type,search=search)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/device/page", response_model=AlerteResumePageResponse)
def liste_device_alerte_page(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    type:Optional[str]=None,
    search:Optional[str]=None,
    date_debut: Optional[datetime] = None,
    date_fin: Optional[datetime] = None,
):
    try:
        return getDeviceAlertesPage(page=page, page_size=page_size,
                                    date_debut=date_debut, date_fin=date_fin,type=type,search=search)
    except Exception as e:
        traceback.print_exc
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{type_alerte}", response_model=AlerteNombreResponse)
def stats_alerte_type(type_alerte: str, statut: str = "active",
                      date_debut: Optional[datetime] = None, date_fin: Optional[datetime] = None):
    try:
        return {"nombre": getNombreAlerteParType(type_alerte, statut, date_debut, date_fin)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nombre/nouvelle", response_model=AlerteNombreResponse)
def nombre_alerte_nouvelle():
    try:
        return {"nombre": getNombreAlerteNouvelle()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nouvelles", response_model=List[AlerteResume])
def nouvelles_alertes(limit: int = Query(10, ge=1, le=50)):
    try:
        return getNouvellesAlertes(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))