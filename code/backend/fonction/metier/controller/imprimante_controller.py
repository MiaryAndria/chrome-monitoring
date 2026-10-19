from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
import traceback

from backend.fonction.metier.service.imprimante_service import (
    get_imprimante,
    get_imprimante_detail,
    get_imprimantes_page,
)
from backend.fonction.metier.models.imprimante import (
    ImprimanteResponse,
    ImprimanteDetailResponse,
    ImprimantePageResponse,
)
from backend.utils.validation import is_valid_datetime_range

router = APIRouter()


@router.get("/liste", response_model=ImprimantePageResponse)
def getImprimantes(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=10000),
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
        return get_imprimantes_page(
            page=page,
            page_size=page_size,
            recherche=recherche,
            datetime_from=datetime_from,
            datetime_to=datetime_to,
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}", response_model=ImprimanteDetailResponse)
def getImprimanteDetail(id: int):
    try:
        result = get_imprimante_detail(id)
        if result is None:
            raise HTTPException(status_code=404, detail="Imprimante introuvable")
        return result
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
