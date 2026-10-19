from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException

from backend.fonction.metier.models.configuration import ConfigurationResponse, ConfigurationData
from backend.fonction.metier.service.configuration_service import (
    InsertConfiguration as insert_config_service,
    UpdateConfiguration as update_config_service,
    deleteConfiguration as delete_config_service,
    getListeArchiveConfiguration,
    getListeConfiguration,
    getDetailConfiguration,
    reStaurer as restore_config_service,
)

router = APIRouter()

@router.get("/liste", response_model=List[ConfigurationResponse])
def get_liste():
    try:
        return getListeConfiguration()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create", status_code=201)
def create_configuration(data: ConfigurationData):
    date = datetime.now()
    insert_config_service(data.type, data.valeur, date)
    return {"message": "Configuration créée"}

@router.get("/{id}",response_model=ConfigurationResponse)
def get_detail(id:int):
    try:
        return getDetailConfiguration(id)
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    
@router.put("/{id}/update")
def update_configuration(id: int, data: ConfigurationData):
    date = datetime.now()
    update_config_service(id, data.type, data.valeur, date)
    return {"message": "Configuration mise à jour"}

@router.post("/{id}/delete", status_code=201)
def delete_configuration(id: int):
    delete_config_service(id, date=datetime.now())
    return {"message": "Configuration supprimée"}

@router.get("/liste/archiver", response_model=List[ConfigurationResponse])
def get_list_archive():
    try:
        return getListeArchiveConfiguration()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{id}/restaurer")
def restore_configuration(id: int):
    try:
        restored_id = restore_config_service(id)
        return {"message": "Configuration restaurée", "id": restored_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))