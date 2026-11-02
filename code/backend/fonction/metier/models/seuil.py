from pydantic import BaseModel
from typing import List
from datetime import datetime

class SeuilData(BaseModel):
    id_type:int
    valeur: int
    sens: str | None = None
    

class SeuilResponse(BaseModel):
    id: int
    id_type: int
    cle: str
    categorie: str | None = None
    valeur: int
    date: datetime | None = None
    sens: str | None = None


class SeuilPageResponse(BaseModel):
    items: List[SeuilResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    
class SeuilCategorieResponse(BaseModel):
    id : int
    categorie : str
    
class SeuilTypeResponse(BaseModel):
    id:int
    type:str

