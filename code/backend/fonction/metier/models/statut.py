from typing import List

from pydantic import BaseModel

class Statut(BaseModel):
    nom:str

class StatutData(BaseModel):
    nom:str

class statutResponse(BaseModel):
    id: int
    nom:str

class StatutPageResponse(BaseModel):
    items: List[statutResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
