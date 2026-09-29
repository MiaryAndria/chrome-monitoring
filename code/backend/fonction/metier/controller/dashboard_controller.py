from typing import List
from fastapi import APIRouter, HTTPException
from backend.fonction.metier.service.statistique_service import getStatistiques
from backend.fonction.metier.models.device import StatistiquesResponse

router = APIRouter()
@router.get("/stats",response_model=StatistiquesResponse)
def getStats():
    try:
        stats_data = getStatistiques()
        return stats_data
    except Exception as e:
        raise HTTPException(status_code=500, detail="Connexion BDD impossible")
