from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Query

from backend.exceptions import NotFoundError
from backend.fonction.metier.models.synchronisation import (
    SynchronisationDetail,
    SynchronisationPageResponse,
)
from backend.fonction.metier.service.synchronisation_service import (
    getListeSynchronisation,
    getDetailSynchronisation,
    getSynchronisationEnCours,
    getStatutsSynchronisation,
)
from backend.utils.validation import valider_plage_datetime

router = APIRouter()


@router.get("/statuts", response_model=List[str])
def statuts():
    return getStatutsSynchronisation()


@router.get("/en-cours", response_model=Optional[SynchronisationDetail])
def en_cours():
    return getSynchronisationEnCours()


@router.get("/liste/page", response_model=SynchronisationPageResponse)
def liste_page(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=10000),
    statut: Optional[str] = None,
    date_debut: Optional[datetime] = None,
    date_fin: Optional[datetime] = None,
    fenetre_debut:Optional[datetime] = None,
    fenetre_fin:Optional[datetime] = None,
):
    valider_plage_datetime(date_debut, date_fin)
    return getListeSynchronisation(page, page_size, statut, date_debut, date_fin,fenetre_debut,fenetre_fin)


@router.get("/{id_sync}", response_model=SynchronisationDetail)
def detail(id_sync: int):
    data = getDetailSynchronisation(id_sync)
    if data is None:
        raise NotFoundError("Synchronisation introuvable")
    return data
