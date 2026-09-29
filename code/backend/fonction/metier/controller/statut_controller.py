from typing import List
from fastapi import APIRouter, HTTPException
from backend.fonction.metier.service.statistique_service import getStatistiques
from backend.fonction.metier.models.statut import statutResponse
from backend.fonction.metier.service.statut_service import getListeStatut

router = APIRouter()
@router.get("/liste", response_model=List[statutResponse])
def getStats():
    try:
        statutListe = getListeStatut()
        return statutListe
    except Exception as e:
        print(f"Erreur réelle: {e}")  
        raise HTTPException(status_code=500, detail=str(e))