from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Query

from backend.exceptions import NotFoundError
from backend.fonction.metier.service.imprimante_service import (
    get_imprimante,
    get_imprimante_detail,
    get_imprimantes_page,
    get_vendors,
)
from backend.fonction.metier.models.imprimante import (
    ImprimanteResponse,
    ImprimanteDetailResponse,
    ImprimantePageResponse,
)
from backend.utils.validation import valider_plage_datetime

router = APIRouter()


@router.get("/liste", response_model=ImprimantePageResponse)
def getImprimantes(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=10000),
    recherche: Optional[str] = None,
    vendor: Optional[str] = None,
    datetime_from: Optional[datetime] = None,
    datetime_to: Optional[datetime] = None,
):
    valider_plage_datetime(datetime_from, datetime_to)
    return get_imprimantes_page(
        page=page,
        page_size=page_size,
        recherche=recherche,
        vendor=vendor,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
    )


@router.get("/vendors", response_model=List[str])
def getVendors():
    return get_vendors()


@router.get("/{id}", response_model=ImprimanteDetailResponse)
def getImprimanteDetail(id: int):
    result = get_imprimante_detail(id)
    if result is None:
        raise NotFoundError("Imprimante introuvable")
    return result
