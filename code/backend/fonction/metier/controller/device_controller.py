from typing import List
from fastapi import APIRouter, HTTPException,Query
from backend.fonction.metier.models.device import DeviceResponses
from backend.fonction.metier.service.device_service import getListeDevice,getDeviceFiltered,getDeviceDetail
import traceback

router = APIRouter()

@router.get("/liste", response_model=List[DeviceResponses])
def getListe():
    try:
        liste = getListeDevice()
        return liste
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=List[DeviceResponses])
def getListeFiltrer(recherche : str = Query(...)):
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