# api/routers/movies.py

"""
Endpoints films : liste paginée et détail par identifiant.
"""

import math

from fastapi import APIRouter, HTTPException, Query

from schemas import FilmResume, MoviesListResponse, PaginationMeta, FilmDetail, MembreEquipe
from database import execute_sql

router = APIRouter(tags=["Movies"])

RESULTS = 10

# --------------------------------------------------------------------------------

