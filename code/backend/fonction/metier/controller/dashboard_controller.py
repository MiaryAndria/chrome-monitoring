from fastapi import APIRouter

from backend.fonction.metier.service.dashboard_service import get_summary
from backend.fonction.metier.models.dashboard import DashboardSummaryResponse

router = APIRouter()


@router.get("/summary", response_model=DashboardSummaryResponse)
def getDashboardSummary():
    return get_summary()
