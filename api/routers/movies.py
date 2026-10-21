# api/routers/movies.py

"""
Endpoints films : liste paginée et détail par identifiant.
"""

import math

from fastapi import APIRouter, HTTPException, Query

from schemas import FilmResume, MoviesListResponse, PaginationMeta, MovieDetail
from database import execute_sql
from utils import split_list

router = APIRouter(tags=["Movies"])

PER_PAGES = 10

# --------------------------------------------------------------------------------

@router.get("/movies/", response_model=MoviesListResponse, summary="Movies List")
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
        print(f"[movies] {type(e).__name__} : {e}")
        raise HTTPException(status_code=500, detail="Internal Error")


@router.get("/movies/{movie_id}", response_model=MovieDetail, summary="Movie detail")
def movie_detail(movie_id: int):
    """
    Retourne toutes les informations disponibles pour un film : ses champs
    de base, ses genres, son équipe (réalisateur(s)/acteurs) et ses tags.
    """
    try:
        movie = execute_sql("movie_detail.sql", (movie_id,))
        
        if not movie:
            raise HTTPException(status_code=404, detail=f"Movie {movie_id} not found.")
        
        film = movie[0]

        film["director"] = split_list(film["director"])
        film["genres"] = split_list(film["genres"])
        film["casting"] = split_list(film["casting"])

        return MovieDetail(**film)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[movies] {type(e).__name__} : {e}")
        raise HTTPException(status_code=500, detail="Internal Error")