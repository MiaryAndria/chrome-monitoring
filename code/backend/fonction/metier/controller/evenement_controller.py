import traceback
from typing import List
from fastapi import APIRouter, HTTPException
from backend.fonction.metier.service.event_service import get_event, get_type_evenement
from backend.fonction.metier.models.evenement import ReponseEvenements, ResponseTypeEvenements

router = APIRouter()


@router.get("/liste", response_model=ReponseEvenements)
def getListe():
    try:
        events = get_event()
        return {"total": len(events), "evenements": events}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/liste/type",response_model=List[ResponseTypeEvenements])
def getListeType():
    try:
        type_evenement = get_type_evenement()
        return type_evenement
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500,detail=str(e))