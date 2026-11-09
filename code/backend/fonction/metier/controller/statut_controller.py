from typing import List
from fastapi import APIRouter, HTTPException, Query

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
    try:
        statutListe = getListeStatut()
        return statutListe
    except Exception as e:
        print(f"Erreur réelle: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/liste/all", response_model=List[statutResponse])
def get_liste_all():
    try:
        return getListeStatutAll()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/liste/page", response_model=StatutPageResponse)
def get_liste_page(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    try:
        return getStatutsPage(page, page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}", response_model=statutResponse)
def get_detail(id: int):
    try:
        statut = getDetailStatut(id)
        if statut is None:
            raise HTTPException(status_code=404, detail="Statut introuvable")
        return statut
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{id}/update")
def update_statut(id: int, data: StatutData):
    try:
        UpdateStatut(id, data.nom)
        return {"message": "Statut mis à jour"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
