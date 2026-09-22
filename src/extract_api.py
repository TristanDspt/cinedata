# extract_api.py

import os
from dotenv import load_dotenv
import pandas as pd
import requests
import time

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")

assert API_KEY, "Missing key : check .env file"


def safe_get(url, retries=3):
    if retries == 0:
        print("Too much tentatives, try again later")
        return None
    try:
        response = requests.get(url, headers=get_headers(), timeout=5)
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


def get_headers():
    return {
        "accept": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }


def get_popular_movie(limit=5):
    url = "https://api.themoviedb.org/3/movie/popular?language=en-US&page=1"
    
    response = safe_get(url)

    if response is not None:
        data = response.json()
        popular_movies = data["results"][:limit]
    else:
        return None

    return popular_movies


# url = "https://api.themoviedb.org/3/movie/movie_id?language=en-US"
def get_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"

    response = safe_get(url)

    if response is not None:
        movie_details = response.json()
    else:
        return None

    return movie_details


# url = "https://api.themoviedb.org/3/movie/movie_id/credits?language=en-US"
def get_casting(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?language=en-US"

    response = safe_get(url)

    if response is not None:
        data = response.json()
        casting = data["cast"]
    else:
        return None

    return casting


def get_genre_table():
    url = f"https://api.themoviedb.org/3/genre/movie/list"

    response = safe_get(url)
    
    if response is not None:
        genre_list = response.json()

    return genre_list


def build_movie_dict():
    popular_movies = get_popular_movie()

    movies = []

    for movie in popular_movies:
        details = get_movie_details(movie["id"])
        casting, directors = get_casting(movie["id"])

        result = {
            "id": movie.get("id"),
            "title": movie.get("title"),
            "tagline": details.get("tagline"),
            "director": [director["name"] for director in directors],
            "casting": [actor["name"] for actor in casting],
            "release": movie.get("release_date"),
            "duration": details.get("runtime"),
            "budget" : details.get("budget"),
            "revenue": details.get("revenue"),
            "genre_ids": movie.get("genre_ids"),
            "genres": [genre["name"] for genre in details.get("genres")],
            "synopsis": movie.get("overview"),
            "vote_average_tmdb": movie.get("vote_average"),
            "vote_count_tmdb": movie.get("vote_count"),
        }
        
        movies.append(result)
        
    return movies
