from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from backend.exceptions import NotFoundError
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
    get_detail_evenement,
    get_evenements_resolues_page,
    marquer_evenement_resolu,
    repasser_evenement_actif,
)
from backend.utils.validation import valider_plage_datetime

router = APIRouter()


@router.get("/liste", response_model=EvenementsPageResponse)
def getListe(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=10000),
    type_evenement: Optional[str] = None,
    id_filiale: Optional[int] = None,
    filiale: Optional[str] = None,
    recherche: Optional[str] = None,
    utilisateur_recent: Optional[str] = None,
    datetime_from: Optional[datetime] = None,
    datetime_to: Optional[datetime] = None,
):
    valider_plage_datetime(datetime_from, datetime_to)
    return get_events_page(
        page=page,
        page_size=page_size,
        type_evenement=type_evenement,
        id_filiale=id_filiale,
        filiale=filiale,
        recherche=recherche,
        utilisateur_recent=utilisateur_recent,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
    )


@router.get("/liste/type", response_model=List[ResponseTypeEvenements])
def getListeType():
    return get_type_evenement()


@router.get("/liste/resolue", response_model=EvenementsPageResponse)
def getListeEvenementsResolues(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=10000),
    type_evenement: Optional[str] = None,
    id_filiale: Optional[int] = None,
    filiale: Optional[str] = None,
    recherche: Optional[str] = None,
    utilisateur_recent: Optional[str] = None,
    datetime_from: Optional[datetime] = None,
    datetime_to: Optional[datetime] = None,
):
    valider_plage_datetime(datetime_from, datetime_to)
    return get_evenements_resolues_page(
        page=page,
        page_size=page_size,
        type_evenement=type_evenement,
        id_filiale=id_filiale,
        filiale=filiale,
        recherche=recherche,
        utilisateur_recent=utilisateur_recent,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
    )


@router.get("/{event_id}/duree-vie")
def getDureeVie(event_id: int):
    resultat = get_duree_vie_evenement(event_id)
    if resultat is None:
        raise NotFoundError("Événement introuvable")
    return resultat


@router.get("/{event_id}")
def getDetailEvenement(event_id: int):
    resultat = get_detail_evenement(event_id)
    if resultat is None:
        raise NotFoundError("Événement introuvable")
    return resultat


@router.post("/{event_id}/marquer-resolu")
def marquerResolu(event_id: int):
    ok = marquer_evenement_resolu(event_id)
    if not ok:
        raise NotFoundError("Événement introuvable")
    return {"ok": True}


@router.post("/{event_id}/repasser-active")
def repasserActive(event_id: int):
    ok = repasser_evenement_actif(event_id)
    if not ok:
        raise NotFoundError("Événement introuvable")
    return {"ok": True}


@router.post("/{event_id}/ia/chat/stream")
def iaChatStream(event_id: int, payload: IAChatRequest):
    generateur = ia_chat_stream(event_id, [m.model_dump() for m in payload.messages])
    if generateur is None:
        raise NotFoundError("Événement introuvable")
    return StreamingResponse(generateur, media_type="text/plain; charset=utf-8")
