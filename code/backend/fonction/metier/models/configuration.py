from pydantic import BaseModel
from typing import Any, List
from datetime import datetime

class ConfigurationData(BaseModel):
    id_type: int
    valeur: Any

class ConfigurationResponse(BaseModel):
    id: int
    id_type: int
    cle: str
    categorie: str | None = None
    valeur: Any
    date: datetime | None = None


class ConfigurationPageResponse(BaseModel):
    items: List[ConfigurationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
class ConfigurationCategorieResponse(BaseModel):
    id : int
    categorie : str
    
class ConfigurationTypeResponse(BaseModel):
    id:int
    type:str
