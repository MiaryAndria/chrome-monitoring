from pydantic import BaseModel
from typing import Any, List
from datetime import datetime

class ConfigurationData(BaseModel):
    type: str
    valeur: Any

class ConfigurationResponse(BaseModel):
    id:int
    type: str
    valeur: Any
    date: datetime | None = None


class ConfigurationPageResponse(BaseModel):
    items: List[ConfigurationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
