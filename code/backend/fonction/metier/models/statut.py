from typing import Optional
from pydantic import BaseModel

class Statut(BaseModel):
    nom:str

class statutResponse(BaseModel):
    id: int
    nom:str
