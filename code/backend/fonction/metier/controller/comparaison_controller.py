import traceback
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from backend.fonction.metier.models.comparaison import (
    ComparaisonSimpleRequest,
    ComparaisonDoubleRequest,
    ComparaisonResponse,
    ComparaisonPageResponse,
)
from backend.fonction.metier.models.device import DeviceVersionResponse
from backend.fonction.metier.service.comparaison_service import (
    comparaisonSimple,
    comparaisonDouble,
    getListeComparaison,
    getComparaisonsPage,
    get_liste_version_device,
    get_comparaison_detail,
)
from backend.fonction.metier.service.export_service import exporter_comparaison
from backend.utils.validation import is_valid_datetime_range

router = APIRouter()


@router.get("/liste", response_model=List[ComparaisonResponse])
def get_liste():
    try:
        return getListeComparaison()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/liste/page", response_model=ComparaisonPageResponse)
def get_liste_page(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    datetime_from: Optional[datetime] = None,
    datetime_to: Optional[datetime] = None,
):
    if not is_valid_datetime_range(datetime_from, datetime_to):
        raise HTTPException(
            status_code=400,
            detail="datetime_to doit être supérieur ou égal à datetime_from",
        )
    try:
        return getComparaisonsPage(page, page_size, datetime_from, datetime_to)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/version/{id}", response_model=List[DeviceVersionResponse])
def get_liste_version(id: int):
    try:
        return get_liste_version_device(id)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simple")
def creer_comparaison_simple(payload: ComparaisonSimpleRequest):
    try:
        return comparaisonSimple(payload.id_device, payload.version_a, payload.version_b)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/double")
def creer_comparaison_double(payload: ComparaisonDoubleRequest):
    try:
        return comparaisonDouble(
            payload.id_device_a, payload.version_a,
            payload.id_device_b, payload.version_b,
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}", response_model=ComparaisonResponse)
def get_comparaison(id: int):
    try:
        detail = get_comparaison_detail(id)
        if detail is None:
            raise HTTPException(status_code=404, detail="Comparaison introuvable")
        return detail
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}/export/{format}")
def export_comparaison(id: int, format: str):
    try:
        detail = get_comparaison_detail(id)
        if detail is None:
            raise HTTPException(status_code=404, detail="Comparaison introuvable")
        if format not in ("pdf", "excel"):
            raise HTTPException(status_code=400, detail="Format invalide (pdf ou excel)")
        buffer, filename, media_type = exporter_comparaison(detail, format)
        return StreamingResponse(
            buffer,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
