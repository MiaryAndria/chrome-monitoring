from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class SynchronisationResume(BaseModel):
    id: int
    source: str
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    fenetre_debut: Optional[datetime] = None
    fenetre_fin: Optional[datetime] = None
    nb_lignes: int = 0
    message: Optional[str] = None
    statut: Optional[str] = None
    date_statut: Optional[datetime] = None
    duree_s: Optional[float] = None


class SynchronisationDetail(SynchronisationResume):
    journal: Optional[dict] = None


class SynchronisationPageResponse(BaseModel):
    items: List[SynchronisationResume]
    total: int
    page: int
    page_size: int
    total_pages: int
