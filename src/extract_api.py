# extract_api.py

import os
from dotenv import load_dotenv
import pandas as pd
import requests
import time
import yaml

load_dotenv()
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = config["api_tmdb"]["base_url"]
TIMEOUT = config["api_tmdb"]["timeout"]

assert API_KEY, "Missing key : check .env file"

# --------------------------------------------------------------------------------
# --                                  EXTRACT                                   --
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


def safe_get(url, retries=3):
    """
    Effectue une requête GET sécurisée avec gestion des erreurs et retry sur 429.

    Args:
        url (str): URL de la requête.
        retries (int): Nombre de tentatives restantes en cas de 429. Défaut : 3.

    Returns:
        Response: Objet response requests, ou None en cas d'erreur.
    """
    if retries == 0:
        print("Too much tentatives, try again later")
        return None
    try:
        response = requests.get(url, headers=get_headers(), timeout=TIMEOUT)
        response.raise_for_status()
        return response
    except requests.exceptions.ConnectionError:
        print("Connexion error.")
    except requests.exceptions.Timeout:
        print("Timeout.")
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 429:
            time_sleep = int(err.response.headers["Retry-After"]) + 1
            time.sleep(time_sleep)
            return safe_get(url, retries - 1)
        else:
            print(f"HTTP error : {err}")
    except requests.exceptions.RequestException as err:
        print(f"Unknown error : {err}")
    return None


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
        response = safe_get(url)
        if response is not None:
            data = response.json()
            movies = data["results"]
            movies_filtered.extend([movie for movie in movies if movie["vote_count"] > 2000])
            page += 1
        else:
            return None

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
    response = safe_get(url)

    if response is not None:
        return response.json()
    return None


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
    response = safe_get(url)

    if response is not None:
        data = response.json()
        casting = data["cast"][:limit]
        crew = data["crew"]
        directors = [person for person in crew if person["job"] == "Director"]
        return casting, directors
    return None


# def get_genre_table():
#     """
#     Récupère la liste des genres TMDB (id -> nom).
#     Utile pour une future version avec table genres séparée en DB.
#
#     Returns:
#         list: Liste de dicts {"id": ..., "name": ...}, ou None en cas d'erreur.
#     """
#     url = "{BASE_URL}/genre/movie/list"
#     response = safe_get(url)
#
#     if response is not None:
#         return response.json().get("genres", [])
#     return None

# --------------------------------------------------------------------------------
# --                                 TRANSFORM                                  --
# --------------------------------------------------------------------------------

def get_missings(top_movies):
    """
    Identifie les films avec des données manquantes (budget, revenue).
    
    Args:
        top_movies (list): Liste de dicts films retournée par get_top_movie().
    
    Returns:
        tuple: (missing_budget, missing_revenue) — deux listes de dicts
               avec les clés 'id', 'title', 'release_date'.
    """
    missing_budget = []
    missing_revenue = []

    for movie in top_movies:
        movie_id = movie["id"]
        details = get_movie_details(movie_id)

        if details is None:
            continue

        if not details.get("budget") or details.get("budget") < 100000:
            missing_budget.append({"id": movie_id, "title": movie["title"], "release_date": movie["release_date"]})
        if not details.get("revenue") or details.get("revenue") < 100000:
            missing_revenue.append({"id": movie_id, "title": movie["title"], "release_date": movie["release_date"]})

    return missing_budget, missing_revenue
