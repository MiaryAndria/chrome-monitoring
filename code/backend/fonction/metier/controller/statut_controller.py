from typing import List
from fastapi import APIRouter, Query

from backend.exceptions import NotFoundError
from backend.fonction.metier.models.statut import StatutData, StatutPageResponse, statutResponse
from backend.fonction.metier.service.statut_service import (
    getListeStatut,
    getListeStatutAll,
    getStatutsPage,
    getDetailStatut,
    UpdateStatut,
)

router = APIRouter()


@router.get("/liste", response_model=List[statutResponse])
def getStats():
    return getListeStatut()


@router.get("/liste/all", response_model=List[statutResponse])
def get_liste_all():
    return getListeStatutAll()


@router.get("/liste/page", response_model=StatutPageResponse)
def get_liste_page(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    return getStatutsPage(page, page_size)


@router.get("/{id}", response_model=statutResponse)
def get_detail(id: int):
    statut = getDetailStatut(id)
    if statut is None:
        raise NotFoundError("Statut introuvable")
    return statut


@router.put("/{id}/update")
def update_statut(id: int, data: StatutData):
    UpdateStatut(id, data.nom)
    return {"message": "Statut mis à jour"}
