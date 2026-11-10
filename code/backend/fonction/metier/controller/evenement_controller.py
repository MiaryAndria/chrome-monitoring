import traceback
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from backend.fonction.metier.models.evenement import (
    EvenementsPageResponse,
    ResponseTypeEvenements,
    IAChatRequest,
)

from backend.fonction.metier.service.event_service import (
    get_events_page,
    get_type_evenement,
    get_duree_vie_evenement,
    ia_chat_stream,
)

from backend.utils.validation import is_valid_datetime_range

router = APIRouter()


@router.get("/liste", response_model=EvenementsPageResponse)
def getListe(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=10000),
    type_evenement: Optional[str] = None,
    id_filiale: Optional[int] = None,
    filiale: Optional[str] = None,
    recherche: Optional[str] = None,
    datetime_from: Optional[datetime] = None,
    datetime_to: Optional[datetime] = None,
):
    if not is_valid_datetime_range(datetime_from, datetime_to):
        raise HTTPException(
            status_code=400,
            detail="datetime_to doit être supérieur ou égal à datetime_from",
        )
    try:
        return get_events_page(
            page=page,
            page_size=page_size,
            type_evenement=type_evenement,
            id_filiale=id_filiale,
            filiale=filiale,
            recherche=recherche,
            datetime_from=datetime_from,
            datetime_to=datetime_to,
        )
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


@router.get("/{event_id}/duree-vie")
def getDureeVie(event_id: int):
    try:
        resultat = get_duree_vie_evenement(event_id)
        if resultat is None:
            raise HTTPException(status_code=404, detail="Événement introuvable")
        return resultat
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{event_id}/ia/chat/stream")
def iaChatStream(event_id: int, payload: IAChatRequest):
    generateur = ia_chat_stream(event_id, [m.model_dump() for m in payload.messages])
    if generateur is None:
        raise HTTPException(status_code=404, detail="Événement introuvable")
    return StreamingResponse(generateur, media_type="text/plain; charset=utf-8")