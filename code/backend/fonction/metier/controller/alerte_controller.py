from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Query

from backend.fonction.metier.service.alerte_service import (getListeDeviceAlerteDateResolue,
    getNombreAlerte,getDernieresAlertes,
    getListeDeviceAlerteDate,getDeviceAlertesPage,getDeviceAlertesResoluesPage,getNombreAlerteNouvelle,getNombreAlerteResolue,getNombreAlerteParType,getNouvellesAlertes,getTypeAlerte,
)
from backend.fonction.metier.models.alerte import (
    AlerteNombreResponse,
    AlerteResponse,
    AlerteResume,
    AlerteResumePageResponse,
)
from backend.utils.validation import valider_plage_datetime

router = APIRouter()


@router.get("/nombre", response_model=AlerteNombreResponse)
def nombre_alerte():
    return {"nombre": getNombreAlerte()}


@router.get("/liste/type", response_model=List[AlerteResponse])
def get_type():
    return getTypeAlerte()


@router.get("/nombre/resolue", response_model=AlerteNombreResponse)
def nombre_alerte_resolue():
    return {"nombre": getNombreAlerteResolue()}


@router.get("/tenAlerte", response_model=List[AlerteResume])
def dix_alertes(limit: int = Query(10, ge=1, le=50)):
    return getDernieresAlertes(limit)


@router.get("/device", response_model=List[AlerteResume])
def liste_device_alerte(date_debut: Optional[datetime] = None, date_fin: Optional[datetime] = None):
    valider_plage_datetime(date_debut, date_fin)
    return getListeDeviceAlerteDate(date_debut, date_fin)


@router.get("/device/resolue", response_model=List[AlerteResume])
def liste_device_alerte_resolue(date_debut: Optional[datetime] = None, date_fin: Optional[datetime] = None):
    valider_plage_datetime(date_debut, date_fin)
    return getListeDeviceAlerteDateResolue(date_debut, date_fin)


@router.get("/device/resolue/page", response_model=AlerteResumePageResponse)
def liste_device_alerte_resolue_page(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=10000),
    type: Optional[str] = None,
    search: Optional[str] = None,
    filiale: Optional[str] = None,
    utilisateur_recent: Optional[str] = None,
    date_debut: Optional[datetime] = None,
    date_fin: Optional[datetime] = None,
):
    valider_plage_datetime(date_debut, date_fin)
    return getDeviceAlertesResoluesPage(
        page=page, page_size=page_size,
        date_debut=date_debut, date_fin=date_fin, type=type, search=search,
        filiale=filiale, utilisateur_recent=utilisateur_recent,
    )


@router.get("/device/page", response_model=AlerteResumePageResponse)
def liste_device_alerte_page(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=10000),
    type: Optional[str] = None,
    search: Optional[str] = None,
    filiale: Optional[str] = None,
    utilisateur_recent: Optional[str] = None,
    date_debut: Optional[datetime] = None,
    date_fin: Optional[datetime] = None,
):
    valider_plage_datetime(date_debut, date_fin)
    return getDeviceAlertesPage(
        page=page, page_size=page_size,
        date_debut=date_debut, date_fin=date_fin, type=type, search=search,
        filiale=filiale, utilisateur_recent=utilisateur_recent,
    )


@router.get("/stats/{type_alerte}", response_model=AlerteNombreResponse)
def stats_alerte_type(
    type_alerte: str,
    id_statut: int = 1,
    date_debut: Optional[datetime] = None,
    date_fin: Optional[datetime] = None,
):
    valider_plage_datetime(date_debut, date_fin)
    return {"nombre": getNombreAlerteParType(type_alerte, id_statut, date_debut, date_fin)}


@router.get("/nombre/nouvelle", response_model=AlerteNombreResponse)
def nombre_alerte_nouvelle():
    return {"nombre": getNombreAlerteNouvelle()}


@router.get("/nouvelles", response_model=List[AlerteResume])
def nouvelles_alertes(limit: int = Query(10, ge=1, le=50)):
    return getNouvellesAlertes(limit)
