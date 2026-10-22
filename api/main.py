# api/main.py
"""
Point d'entrée de l'API CinéData.

Lancement (depuis la racine du projet, sans se déplacer dans api/) :
    uvicorn main:app --reload --app-dir api

Équivalent en se plaçant dans le dossier :
    cd api
    uvicorn main:app --reload

Documentation Swagger : http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from routers import system, movies, recommendation

# --------------------------------------------------------------------------------

TAGS_METADATA = [
    {"name": "System", "description": "État de l'API et informations générales."},
    {"name": "Movies", "description": "Liste et détail des films du catalogue."},
    {"name": "Recommendation", "description": "Films proches d'un film donné, calculés par similarité de contenu (genres, réalisateurs, casting, slogan, synopsis)."},
]

app = FastAPI(
    title="CinéData API",
    description="API d'exposition des données du projet CinéData.",
    version="1.0.0",
    openapi_tags=TAGS_METADATA,
)

app.include_router(system.router)
app.include_router(movies.router)
app.include_router(recommendation.router)