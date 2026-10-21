from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from backend.fonction.metier.service.comparaison_service import 



router = APIRouter()

@router.get("/liste", response_model=List[ComparaisonResponse])
def get_liste():
    try:
        return getListeComparaison()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

