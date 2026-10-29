from datetime import datetime
from typing import List
from pydantic import BaseModel


class UserLogin(BaseModel):
    email: str
    mdp: str


class UserSignin(BaseModel):
    nom: str
    email: str
    mdp: str


class UserRoleUpdate(BaseModel):
    id_role: int


class UserResponse(BaseModel):
    id: int
    nom: str
    email: str
    id_role: int
    role: str | None = None
    date: datetime | None = None


class UserPageResponse(BaseModel):
    items: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class MeResponse(BaseModel):
    id: int
    email: str
    id_role: int
