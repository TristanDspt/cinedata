# src/extract_api.py*

"""
Extraction des films depuis l'API TMDB : sélection des mieux notés, récupération
des détails et du casting, puis sauvegarde en JSON (data/raw/tmdb.json).

Les films dont le budget ou le revenu est absent ou trop faible pour être
fiable sont aussi listés à part (clé "missing") afin d'être complétés
ensuite via le scraping Wikipedia (voir extract_web.py).
"""

import os
import json
from config import API_KEY, BASE_TMDB_URL, TMDB_RAW
from utils import safe_get

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

    # TMDB pagine ses résultats ; on avance page par page jusqu'à réunir assez
    # de films ayant un nombre de votes significatif (> 2000), avec une borne
    # de sécurité à 1000 pages pour éviter une boucle infinie
    while len(movies_filtered) < limit and page <= 1000:
        url = f"{BASE_TMDB_URL}/movie/top_rated?language=en-US&page={page}"
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
    url = f"{BASE_TMDB_URL}/movie/{movie_id}?language=en-US"
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
    url = f"{BASE_TMDB_URL}/movie/{movie_id}/credits?language=en-US"
    response = safe_get(url, headers=get_headers())

    if response is None:
        return None
    
    data = response.json()
    casting = data["cast"][:limit]
    crew = data["crew"]
    directors = [person for person in crew if person["job"] == "Director"]

    return casting, directors

# --------------------------------------------------------------------------------

def extract_tmdb(limit=5, force_refresh=False):
    """
    Extrait les films les mieux notés de TMDB avec leurs détails et casting.
    
    Args:
        limit (int): Nombre de films à extraire. Défaut : 5.
    
    Returns:
        list: Liste de dicts films enrichis, ou None en cas d'erreur.
    """
    if os.path.exists(TMDB_RAW) and not force_refresh:
        with open(TMDB_RAW, "r") as f:
            extract_json = json.load(f)
    else:
        top_movies = get_top_movie(limit=limit)
        movies = []
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

            # En dessous de 100 000, le budget/revenu TMDB est considéré comme
            # non renseigné ou pas assez fiable : le film est marqué "missing"
            # pour être complété plus tard via Wikipedia
            missing_fields = []
            if not details.get("budget") or details.get("budget") < 100_000:
                missing_fields.append("budget")
            if not details.get("revenue") or details.get("revenue") < 100_000:
                missing_fields.append("revenue")

            if missing_fields:
                missing.append({"id": movie_id, "title": movie["title"], "release_date": movie["release_date"], "missing_fields": missing_fields})

            movies.append({
                "id": movie_id,
                "title": movie.get("title"),
                "tagline": details.get("tagline"),
                "release_date": movie.get("release_date"),
                "budget": details.get("budget"),
                "revenue": details.get("revenue"),
                "duration": details.get("runtime"),
                "genres": [genre["name"] for genre in details.get("genres")],
                "casting": [actor["name"] for actor in casting],
                "directors": [director["name"] for director in directors],
                "synopsis": details.get("overview"),
                "vote_average_tmdb": movie.get("vote_average"),
                "vote_count_tmdb": movie.get("vote_count"),
            })

        extract_json = {"movies": movies, "missing": missing}
        with open(TMDB_RAW, "w") as f:
            json.dump(extract_json, f)

    return extract_json