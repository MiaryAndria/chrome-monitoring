import traceback
from typing import List

from fastapi import APIRouter, HTTPException

from backend.fonction.metier.models.comparaison import (
    ComparaisonSimpleRequest,
    ComparaisonDoubleRequest,
    ComparaisonResponse,
)
from backend.fonction.metier.models.device import DeviceVersionResponse
from backend.fonction.metier.service.comparaison_service import (
    comparaisonSimple,
    comparaisonDouble,
    getListeComparaison,
    get_liste_version_device,
)

router = APIRouter()


@router.get("/liste", response_model=List[ComparaisonResponse])
def get_liste():
    try:
        return getListeComparaison()
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
