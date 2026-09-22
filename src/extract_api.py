import os
from dotenv import load_dotenv
import requests

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def safe_get(url):
    try:
        response = requests.get(url, headers=get_headers(), timeout=5)
        response.raise_for_status()
        return response
    except requests.exceptions.ConnectionError:
        print("Connexion error.")
    except requests.exceptions.Timeout:
        print("Timeout.")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error : {err}")
    except requests.exceptions.RequestException as err:
        print(f"Unknown error : {err}")
    return None

def get_headers():
    return {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_API_KEY}"
    }

def get_popular_movie():
    url = "https://api.themoviedb.org/3/movie/popular?language=en-US&page=1"
    
    response = safe_get(url)

    if response is not None:
        data = response.json()
        popular_movies = data["results"]
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
def get_casting(movie_id, limit=5):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?language=en-US"

    response = safe_get(url)

    if response is not None:
        data = response.json()
        casting = data["cast"]
    else:
        return None

    return casting

