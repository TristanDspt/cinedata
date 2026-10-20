# api/schemas.py

"""
Modèles Pydantic de l'API — définissent la forme des données en entrée/sortie
et sont validés automatiquement par FastAPI.

Approche volontairement simple : des classes à plat (attributs typés),
pas d'héritage ni de validateurs personnalisés — cohérent avec une
introduction encore récente à la POO.
"""

from typing import Optional
from pydantic import BaseModel
from datetime import date


# System

class InfoResponse(BaseModel):
    nom: str
    version: str
    description: str


class HealthResponse(BaseModel):
    status: str

# Movies

class FilmResume(BaseModel):
    id: int
    title: str
    release_date: Optional[date] = None

class PaginationMeta(BaseModel):
    page: int
    per_pages: int
    total: int
    total_pages: int

class MoviesListResponse(BaseModel):
    pagination: PaginationMeta
    results: list[FilmResume]