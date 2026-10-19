from fastapi import APIRouter, HTTPException

from backend.fonction.metier.service.dashboard_service import (
    get_summary,
    getStatistiques,
)
from backend.fonction.metier.models.device import StatistiquesResponse
from backend.fonction.metier.models.dashboard import DashboardSummaryResponse

router = APIRouter()


@router.get("/stats", response_model=StatistiquesResponse)
def getStats():
    try:
        stats_data = getStatistiques()
        return stats_data
    except Exception as e:
        raise HTTPException(status_code=500, detail="Connexion BDD impossible")


@router.get("/summary", response_model=DashboardSummaryResponse)
def getDashboardSummary():
    try:
        return get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
