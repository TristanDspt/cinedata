# api/routers/recommendation.py

"""
Endpoint de recommandation : films proches d'un film donné.
"""

from fastapi import APIRouter, HTTPException

from schemas import RecommendationResponse, RecommendedMovie
from database import execute_sql
from reco_engine import recommend
from utils import split_list

router = APIRouter(tags=["Recommendation"])

# --------------------------------------------------------------------------------

@router.get("/recommendation/{movie_id}", response_model=RecommendationResponse, summary="Movie recommendation")
def movie_recommendation(movie_id: int):
    """
    Retourne les films les plus proches d'un film (genres, réalisateurs,
    casting, slogan, synopsis), du plus proche au moins proche.
    """
    try:
        recommendations = recommend(movie_id)

        if recommendations is None:
            raise HTTPException(status_code=404, detail=f"Movie {movie_id} not found.")

        movies = []
        for reco_id, score in recommendations:
            rows = execute_sql("movie_detail.sql", (reco_id,))
            if not rows:
                continue

            movie = rows[0]
            movie["directors"] = split_list(movie["directors"])
            movie["genres"] = split_list(movie["genres"])
            movie["casting"] = split_list(movie["casting"])

            movies.append(RecommendedMovie(**movie, score=score))

        return RecommendationResponse(movie_id=movie_id, recommendations=movies)

    except HTTPException:
        raise
    except Exception as e:
        print(f"[recommendation] {type(e).__name__} : {e}")
        raise HTTPException(status_code=500, detail="Internal Error")