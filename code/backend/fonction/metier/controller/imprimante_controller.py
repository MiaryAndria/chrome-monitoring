from typing import List
from fastapi import APIRouter, HTTPException
from backend.fonction.metier.service.imprimante_service import get_imprimante
from backend.fonction.metier.models.imprimante import ImprimanteResponse
router = APIRouter()
import traceback

@router.get("/liste", response_model=List[ImprimanteResponse])
def getImprimantes():
    try:
        return get_imprimante()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))