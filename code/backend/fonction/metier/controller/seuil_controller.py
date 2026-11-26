from typing import List
from fastapi import APIRouter, Query

from backend.exceptions import NotFoundError
from backend.fonction.metier.models.seuil import (
    SeuilCategorieResponse,
    SeuilResponse,
    SeuilData,
    SeuilPageResponse,
    SeuilTypeResponse,
    SeuilLimiteUpdate,
)
from backend.fonction.metier.service.seuil_service import (
    InsertSeuil as insert_seuil_service,
    UpdateSeuil as update_seuil_service,
    deleteSeuil as delete_seuil_service,
    hardDeleteSeuil as hard_delete_seuil_service,
    get_liste_categorie_seuil,
    get_liste_type_seuil_tous,
    get_liste_type_seuil_by_categorie,
    getListeArchiveSeuil,
    getListeSeuil,
    getSeuilsPage,
    getSeuilsArchivePage,
    getDetailSeuil,
    reStaurer as restore_seuil_service,
    update_limite_seuil_type,
)

router = APIRouter()


@router.get("/liste", response_model=List[SeuilResponse])
def get_liste():
    return getListeSeuil()


@router.get("/liste/page", response_model=SeuilPageResponse)
def get_liste_page(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=10000), categorie: str | None = None, type: str | None = None):
    return getSeuilsPage(page=page, page_size=page_size, categorie=categorie, type_=type)


@router.get("/liste/archiver", response_model=List[SeuilResponse])
def get_list_archive():
    return getListeArchiveSeuil()


@router.get("/liste/archiver/page", response_model=SeuilPageResponse)
def get_list_archive_page(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=10000)):
    return getSeuilsArchivePage(page=page, page_size=page_size)


@router.get("/categorie/type", response_model=List[SeuilCategorieResponse])
def get_liste_categorie():
    return get_liste_categorie_seuil()


@router.get("/type/tous", response_model=List[SeuilTypeResponse])
def get_liste_type_tous():
    return get_liste_type_seuil_tous()


@router.get("/type/{id_categorie}", response_model=List[SeuilTypeResponse])
def get_liste_type(id_categorie: int):
    return get_liste_type_seuil_by_categorie(id_categorie)

@router.put("/type/{id_type}/limite", response_model=SeuilTypeResponse)
def update_limite_type(id_type: int, data: SeuilLimiteUpdate):
    return update_limite_seuil_type(id_type, data.limite)


@router.post("/create", status_code=201)
def create_seuil(data: SeuilData):
    insert_seuil_service(data.id_type, data.valeur)
    return {"message": "Seuil créé"}


@router.get("/{id}", response_model=SeuilResponse)
def get_detail(id: int):
    detail = getDetailSeuil(id)
    if detail is None:
        raise NotFoundError("Seuil introuvable")
    return detail


@router.put("/{id}/update")
def update_seuil(id: int, data: SeuilData):
    update_seuil_service(id, data.valeur, sens=data.sens)
    return {"message": "Seuil mis à jour"}


@router.post("/{id}/delete", status_code=201)
def delete_seuil(id: int):
    delete_seuil_service(id)
    return {"message": "Seuil supprimé"}


@router.post("/{id}/hard/delete")
def hard_delete_seuil(id: int):
    supprime = hard_delete_seuil_service(id)
    if not supprime:
        raise NotFoundError("Seuil introuvable")
    return {"message": "Seuil supprimé définitivement"}


@router.post("/{id}/restaurer")
def restore_seuil(id: int):
    restored_id = restore_seuil_service(id)
    return {"message": "Seuil restauré", "id": restored_id}

    
