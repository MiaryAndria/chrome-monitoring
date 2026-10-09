from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException,Query
from backend.fonction.metier.models.configuration import ConfigurationResponse,ConfigurationData
from backend.fonction.metier.service.configuration_service import getListeConfiguration,getDetailConfiguration,InsertConfiguration,UpdateConfiguration
import traceback

router = APIRouter()

@router.get("/liste", response_model=List[ConfigurationResponse])
def getListe():
    try:
        liste = getListeConfiguration()
        return liste
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}", response_model=ConfigurationResponse)
def getDetailDevice(id):
    try:
        device = getDetailConfiguration(id)

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
        
        
@router.post("/create", status_code=201)
def create(data: ConfigurationData):
    date = datetime.now()
    InsertConfiguration(data.type, data.valeur,date)
    return {"message": "Configuration créée"}

@router.put("/{id}/update")
def update(id: int, data: ConfigurationData):
    date = datetime.now()
    UpdateConfiguration(data.type, data.valeur, date, id)
    return {"message": "Configuration mise à jour"}