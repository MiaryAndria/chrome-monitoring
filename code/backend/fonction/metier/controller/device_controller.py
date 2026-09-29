from typing import List
from fastapi import APIRouter, HTTPException,Query
from backend.fonction.metier.models.device import DeviceResponses
from backend.fonction.metier.service.device_service import synchroniser_tout,reset_data,getListeDevice,getDeviceFiltered
from backend.fonction.metier.service.device_service import getDeviceDetail

router = APIRouter()

@router.post("/synch")
def synchDevices():
    try:
        synchroniser_tout()
        return {"message": "Synchronisation terminée avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
def resetAll():
    try:
        reset_data()
        return {"message": "Suppression terminée avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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

@router.get("/{id}",response_model=DeviceResponses)
def getDetailDevice(id):
    try:
        device = getDeviceDetail(id)
        if device is None :
                raise HTTPException(
                    status_code=404,
                    detail="Device introuvable"
            )
        return device 
        
    except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        