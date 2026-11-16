from typing import List
from fastapi import APIRouter, Query

from backend.exceptions import NotFoundError
from backend.fonction.metier.models.configuration import (
    ConfigurationResponse,
    ConfigurationData,
    ConfigurationPageResponse,
    ConfigurationCategorieResponse,
    ConfigurationTypeResponse,
)
from backend.fonction.metier.service.configuration_service import (
    InsertConfiguration as insert_config_service,
    UpdateConfiguration as update_config_service,
    deleteConfiguration as delete_config_service,
    hardDeleteConfiguration as hard_delete_config_service,
    getListeArchiveConfiguration,
    getListeConfiguration,
    getConfigurationsPage,
    getConfigurationsArchivePage,
    getDetailConfiguration,
    get_liste_categorie_configuration,
    get_liste_type_configuration_by_categorie,
    reStaurer as restore_config_service,
)

router = APIRouter()


@router.get("/liste", response_model=List[ConfigurationResponse])
def get_liste():
    return getListeConfiguration()


@router.get("/liste/page", response_model=ConfigurationPageResponse)
def get_liste_page(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), categorie: str | None = None):
    return getConfigurationsPage(page=page, page_size=page_size, categorie=categorie)


@router.get("/liste/archiver", response_model=List[ConfigurationResponse])
def get_list_archive():
    return getListeArchiveConfiguration()


@router.get("/liste/archiver/page", response_model=ConfigurationPageResponse)
def get_list_archive_page(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    return getConfigurationsArchivePage(page=page, page_size=page_size)


@router.get("/categorie/type", response_model=List[ConfigurationCategorieResponse])
def get_liste_categorie():
    return get_liste_categorie_configuration()


@router.get("/type/{id_categorie}", response_model=List[ConfigurationTypeResponse])
def get_liste_type(id_categorie: int):
    return get_liste_type_configuration_by_categorie(id_categorie)


@router.post("/create", status_code=201)
def create_configuration(data: ConfigurationData):
    insert_config_service(data.id_type, data.valeur)
    return {"message": "Configuration créée"}


@router.get("/{id}", response_model=ConfigurationResponse)
def get_detail(id: int):
    return getDetailConfiguration(id)


@router.put("/{id}/update")
def update_configuration(id: int, data: ConfigurationData):
    update_config_service(id, data.valeur)
    return {"message": "Configuration mise à jour"}


@router.post("/{id}/delete", status_code=201)
def delete_configuration(id: int):
    delete_config_service(id)
    return {"message": "Configuration supprimée"}


@router.post("/{id}/hard/delete")
def hard_delete_configuration(id: int):
    supprime = hard_delete_config_service(id)
    if not supprime:
        raise NotFoundError("Configuration introuvable")
    return {"message": "Configuration supprimée définitivement"}


@router.post("/{id}/restaurer")
def restore_configuration(id: int):
    restored_id = restore_config_service(id)
    return {"message": "Configuration restaurée", "id": restored_id}
