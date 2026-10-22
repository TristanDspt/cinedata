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
    result: list[FilmResume]

class MovieDetail(BaseModel):
    id: int
    title: str
    tagline: Optional[str] = None
    directors: list[str]
    casting: list[str]
    release_date: str
    duration: int
    budget: Optional[int] = None
    revenue: Optional[int] = None
    genres: list[str]
    synopsis: Optional[str] = None
    vote_average_tmdb: Optional[float] = None
    vote_count_tmdb: Optional[int] = None
    vote_average_ml: Optional[float] = None
    vote_count_ml: Optional[int] = None