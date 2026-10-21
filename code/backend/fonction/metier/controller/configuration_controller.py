from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query

from backend.fonction.metier.models.configuration import (
    ConfigurationResponse,
    ConfigurationData,
    ConfigurationPageResponse,
)
from backend.fonction.metier.service.configuration_service import (
    InsertConfiguration as insert_config_service,
    UpdateConfiguration as update_config_service,
    deleteConfiguration as delete_config_service,
    getListeArchiveConfiguration,
    getListeConfiguration,
    getConfigurationsPage,
    getConfigurationsArchivePage,
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


@router.get("/liste/page", response_model=ConfigurationPageResponse)
def get_liste_page(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    try:
        return getConfigurationsPage(page=page, page_size=page_size)
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


@router.get("/liste/archiver/page", response_model=ConfigurationPageResponse)
def get_list_archive_page(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    try:
        return getConfigurationsArchivePage(page=page, page_size=page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{id}/restaurer")
def restore_configuration(id: int):
    try:
        restored_id = restore_config_service(id)
        return {"message": "Configuration restaurée", "id": restored_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))