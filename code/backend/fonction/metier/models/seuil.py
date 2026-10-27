from pydantic import BaseModel
from typing import List
from datetime import datetime

class SeuilData(BaseModel):
    cle: str
    valeur: int


class SeuilResponse(BaseModel):
    id: int
    cle: str
    valeur: int
    date: datetime | None = None


class SeuilPageResponse(BaseModel):
    items: List[SeuilResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
