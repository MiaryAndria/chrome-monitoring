import traceback
from typing import List
from fastapi import APIRouter, HTTPException
from backend.fonction.metier.service.event_service import get_event
from backend.fonction.metier.models.evenement import ReponseEvenements

router = APIRouter()


@router.get("/liste", response_model=ReponseEvenements)
def getListe():
    try:
        events = get_event()
        return {"total": len(events), "evenements": events}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))