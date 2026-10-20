# api/routers/movies.py

"""
Endpoints films : liste paginée et détail par identifiant.
"""

import math

from fastapi import APIRouter, HTTPException, Query

from schemas import FilmResume, MoviesListResponse, PaginationMeta
from database import execute_sql

router = APIRouter(tags=["Movies"])

PER_PAGES = 10

# --------------------------------------------------------------------------------

@router.get("/movie/", response_model=MoviesListResponse, summary="Movies List")
def liste_films(page: int = Query(1, ge=1, description="Page number, start from 1")):
    """
    Retourne les films par pages de 10 (id, titre, année de sortie).
    """
    offset = (page - 1) * PER_PAGES

    try:
        result = execute_sql("movies_list.sql", (PER_PAGES, offset))
        total = execute_sql("movies_count.sql")[0]["total"]
        total_pages = math.ceil(total / PER_PAGES) if total else 0

        return MoviesListResponse(
            pagination=PaginationMeta(page=page, per_pages=PER_PAGES, total=total, total_pages=total_pages),
            result=[FilmResume(**line) for line in result]
        )
    except Exception as e:
        return print(f"[health] {type(e).__name__} : {e}")

