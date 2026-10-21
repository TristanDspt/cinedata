# api/routers/system.py

"""
Endpoints système : info et health.
"""

from fastapi import APIRouter

from schemas import InfoResponse, HealthResponse
from database import execute_sql

# --------------------------------------------------------------------------------

router = APIRouter(tags=["System"])


@router.get("/info", response_model=InfoResponse, summary="API Infos")
def info():
    """Renvoie le nom, la version et une description de l'API."""
    return InfoResponse(
        nom="CinéData API",
        version="1.0.0",
        description="API d'exposition des données du projet CinéData (films, genres, équipe, classements).",
    )


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health():
    """Vérifie que l'API répond et que la base de données est accessible."""
    try:
        execute_sql("movies_count.sql")
        return HealthResponse(status="ok")
    except Exception as e:
        print(f"[health] {type(e).__name__} : {e}")
        return HealthResponse(status="degraded")