from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.fonction.metier.models.evenement import IAChatRequest
from backend.fonction.metier.service.ia_global_service import stream_general_chat

router = APIRouter()


@router.post("/chat/stream")
def iaGlobalChatStream(payload: IAChatRequest):
    generateur = stream_general_chat([m.model_dump() for m in payload.messages])
    return StreamingResponse(generateur, media_type="text/plain; charset=utf-8")
