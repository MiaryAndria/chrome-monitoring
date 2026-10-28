from fastapi import APIRouter, HTTPException

from backend.fonction.metier.service.dashboard_service import get_summary
from backend.fonction.metier.models.dashboard import DashboardSummaryResponse

router = APIRouter()


@router.get("/summary", response_model=DashboardSummaryResponse)
def getDashboardSummary():
    try:
        return get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
