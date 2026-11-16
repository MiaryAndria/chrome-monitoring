from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from backend.exceptions import NotFoundError, ValidationError
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
from backend.utils.validation import valider_plage_datetime

router = APIRouter()


@router.get("/liste", response_model=List[ComparaisonResponse])
def get_liste():
    return getListeComparaison()


@router.get("/liste/page", response_model=ComparaisonPageResponse)
def get_liste_page(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    datetime_from: Optional[datetime] = None,
    datetime_to: Optional[datetime] = None,
):
    valider_plage_datetime(datetime_from, datetime_to)
    return getComparaisonsPage(page, page_size, datetime_from, datetime_to)


@router.get("/version/{id}", response_model=List[DeviceVersionResponse])
def get_liste_version(id: int):
    return get_liste_version_device(id)


@router.post("/simple")
def creer_comparaison_simple(payload: ComparaisonSimpleRequest):
    return comparaisonSimple(payload.id_device, payload.version_a, payload.version_b)


@router.post("/double")
def creer_comparaison_double(payload: ComparaisonDoubleRequest):
    return comparaisonDouble(
        payload.id_device_a, payload.version_a,
        payload.id_device_b, payload.version_b,
    )


@router.get("/{id}", response_model=ComparaisonResponse)
def get_comparaison(id: int):
    detail = get_comparaison_detail(id)
    if detail is None:
        raise NotFoundError("Comparaison introuvable")
    return detail


@router.get("/{id}/export/{format}")
def export_comparaison(id: int, format: str):
    detail = get_comparaison_detail(id)
    if detail is None:
        raise NotFoundError("Comparaison introuvable")
    if format not in ("pdf", "excel"):
        raise ValidationError("Format invalide (pdf ou excel)")
    buffer, filename, media_type = exporter_comparaison(detail, format)
    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
