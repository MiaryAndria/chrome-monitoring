from typing import List
from fastapi import APIRouter, HTTPException, Query

from backend.fonction.metier.models.seuil import (
    SeuilResponse,
    SeuilData,
    SeuilPageResponse,
)
from backend.fonction.metier.service.seuil_service import (
    InsertSeuil as insert_seuil_service,
    UpdateSeuil as update_seuil_service,
    deleteSeuil as delete_seuil_service,
    getListeArchiveSeuil,
    getListeSeuil,
    getSeuilsPage,
    getSeuilsArchivePage,
    getDetailSeuil,
    reStaurer as restore_seuil_service,
)

router = APIRouter()


@router.get("/liste", response_model=List[SeuilResponse])
def get_liste():
    try:
        return getListeSeuil()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/liste/page", response_model=SeuilPageResponse)
def get_liste_page(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    try:
        return getSeuilsPage(page=page, page_size=page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/liste/archiver", response_model=List[SeuilResponse])
def get_list_archive():
    try:
        return getListeArchiveSeuil()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/liste/archiver/page", response_model=SeuilPageResponse)
def get_list_archive_page(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    try:
        return getSeuilsArchivePage(page=page, page_size=page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create", status_code=201)
def create_seuil(data: SeuilData):
    try:
        insert_seuil_service(data.cle, data.valeur)
        return {"message": "Seuil créé"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}", response_model=SeuilResponse)
def get_detail(id: int):
    try:
        return getDetailSeuil(id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{id}/update")
def update_seuil(id: int, data: SeuilData):
    try:
        update_seuil_service(id, data.cle, data.valeur)
        return {"message": "Seuil mis à jour"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{id}/delete", status_code=201)
def delete_seuil(id: int):
    try:
        delete_seuil_service(id)
        return {"message": "Seuil supprimé"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{id}/restaurer")
def restore_seuil(id: int):
    try:
        restored_id = restore_seuil_service(id)
        return {"message": "Seuil restauré", "id": restored_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
