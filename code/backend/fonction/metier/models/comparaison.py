from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ComparaisonSimpleRequest(BaseModel):
    id_device: int
    version_a: str
    version_b: str


class ComparaisonDoubleRequest(BaseModel):
    id_device_a: int
    version_a: str
    id_device_b: int
    version_b: str


class ComparaisonResponse(BaseModel):
    id: int
    id_device_a: Optional[int] = None
    id_device_b: Optional[int] = None
    device_a: Optional[str] = None
    version_a: Optional[str] = None
    device_b: Optional[str] = None
    version_b: Optional[str] = None
    id_type_comparaison: int
    date_reference_a: Optional[datetime] = None
    date_reference_b: Optional[datetime] = None
    date_comparaison: Optional[datetime] = None
    resultat: Optional[dict] = None


class ComparaisonPageResponse(BaseModel):
    items: List[ComparaisonResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
