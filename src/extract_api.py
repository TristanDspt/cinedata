# extract_api.py

import os
from dotenv import load_dotenv
import yaml
import json

from utils import safe_get

# --------------------------------------------------------------------------------

load_dotenv()
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = config["api_tmdb"]["base_url"]

assert API_KEY, "Missing key : check .env file"

# --------------------------------------------------------------------------------

def get_headers():
    """
    Construit les headers d'authentification pour l'API TMDB.

    Returns:
        dict: Headers avec Accept et Authorization Bearer.
    """
    return {
        "accept": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }


def get_top_movie(limit=5):
    """
    Récupère les films les mieux notés sur TMDB, filtrés par nombre de votes.
    
    Args:
        limit (int): Nombre de films à retourner. Défaut : 5.
    
    Returns:
        list: Liste de dicts films, ou None en cas d'erreur.
    """
    page = 1
    movies_filtered = []
    
    while len(movies_filtered) < limit and page <= 1000:
        url = f"{BASE_URL}/movie/top_rated?language=en-US&page={page}"
        response = safe_get(url, headers=get_headers())
        
        if response is None:
            return None
        
        data = response.json()
        movies = data["results"]
        movies_filtered.extend([movie for movie in movies if movie["vote_count"] > 2000])
        page += 1

    return movies_filtered[:limit]


def get_movie_details(movie_id):
    """
    Récupère les détails d'un film TMDB par son identifiant.
    
    Args:
        movie_id (int): Identifiant TMDB du film.
    
    Returns:
        dict: Détails du film, ou None en cas d'erreur.
    """
    url = f"{BASE_URL}/movie/{movie_id}?language=en-US"
    response = safe_get(url, headers=get_headers())

    if response is None:
        return None
    
    return response.json()


def get_casting(movie_id, limit=5):
    """
    Récupère le casting et le(s) réalisateur(s) d'un film TMDB.
    
    Args:
        movie_id (int): Identifiant TMDB du film.
        limit (int): Nombre d'acteurs à retourner. Défaut : 5.
    
    Returns:
        tuple: (casting, directors) — deux listes de dicts, ou None en cas d'erreur.
    """
    url = f"{BASE_URL}/movie/{movie_id}/credits?language=en-US"
    response = safe_get(url, headers=get_headers())

    if response is None:
        return None
    
    data = response.json()
    casting = data["cast"][:limit]
    crew = data["crew"]
    directors = [person for person in crew if person["job"] == "Director"]

    return casting, directors

# --------------------------------------------------------------------------------

def extract_tmdb(limit=5):
    """
    Extrait les films les mieux notés de TMDB avec leurs détails et casting.
    
    Args:
        limit (int): Nombre de films à extraire. Défaut : 5.
    
    Returns:
        list: Liste de dicts films enrichis, ou None en cas d'erreur.
    """
    top_movies = get_top_movie(limit=limit)
    enriched_movies = []
    missing = []

    for movie in top_movies:
        movie_id = movie["id"]
        
        details = get_movie_details(movie_id)
        if details is None:
            continue

        result = get_casting(movie_id)
        if result is None:
            continue

        casting, directors = result
        if casting is None or directors is None:
            continue

        missing_fields = []
        if not details.get("budget") or details.get("budget") < 100000:
            missing_fields.append("budget")
        if not details.get("revenue") or details.get("revenue") < 100000:
            missing_fields.append("revenue")

        if missing_fields:
            missing.append({"id": movie_id, "title": movie["title"], "release_date": movie["release_date"], "missing_fields": missing_fields})

        enriched_movies.append({
            "id": movie_id,
            "title": movie.get("title"),
            "release_date": movie.get("release_date"),
            "budget": details.get("budget"),
            "revenue": details.get("revenue"),
            "genres": [genre["name"] for genre in details.get("genres")],
            "casting": [actor["name"] for actor in casting],
            "directors": [director["name"] for director in directors],
            "vote_average_tmdb": movie.get("vote_average"),
            "vote_count_tmdb": movie.get("vote_count"),
        })

    with open("raw_tmdb.json", "w") as f:
        json.dump(enriched_movies, f)

    return enriched_movies, missing