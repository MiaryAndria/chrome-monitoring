from pydantic import BaseModel
from typing import Optional, List


class EvenementResponse(BaseModel):
    id: int
    date_evenement: Optional[str] = None
    type_evenement: Optional[str] = None
    device_id: Optional[str] = None
    serial_number: Optional[str] = None
    modele: Optional[str] = None
    filiale: Optional[str] = None
    # Champs extraits du JSON details
    cause_class: Optional[str] = None
    cause_hint: Optional[str] = None
    last_user: Optional[str] = None
    incident_key: Optional[str] = None
    crash_seq: Optional[int] = None
    raw_events: Optional[int] = None
    minutes_since_boot: Optional[float] = None


class ReponseEvenements(BaseModel):
    total: int
    evenements: List[EvenementResponse]