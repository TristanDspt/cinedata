"""load_to_db.py

Fusionne les données issues de TMDB, MovieLens (CSV) et Wikipedia en une
liste de dictionnaires "films" prête à être chargée en base de données.

Wikipedia sert de source de secours pour le budget et les revenus quand
TMDB ne les fournit pas, et MovieLens complète les notes/votes (vote_average_ml,
vote_count_ml) via la correspondance sur l'identifiant TMDB (tmdbId).
"""

import os
import yaml
import sqlite3

# --------------------------------------------------------------------------------
# Chargement de la configuration (chemins des fichiers de données brutes)
# --------------------------------------------------------------------------------

BASE_DIR = os.path.dirname(__file__)
config_path = os.path.join(BASE_DIR, "config.yaml")

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

TMDB_RAW = config["path"]["raw_tmdb"]
WIKI_RAW = config["path"]["raw_wiki"]
SCHEMA = config["database"]["schema"]
DB = config["database"]["file"]

# --------------------------------------------------------------------------------

def build_movie_dict(tmdb_data, df, wiki_data):
    """Construit la liste des films enrichis à partir des trois sources de données.

    Le budget et les revenus viennent de TMDB par défaut ; pour les films où
    TMDB ne les fournissait pas, on utilise la valeur récupérée sur Wikipedia
    (enrichissement). Les notes MovieLens sont ajoutées par jointure sur
    l'identifiant TMDB.

    Args:
        tmdb_data (dict): Données brutes TMDB, sous la clé "movies" (liste de films).
        df (pandas.DataFrame): Données MovieLens, doit contenir les colonnes
            "tmdbId", "vote_average_ml" et "vote_count_ml".
        wiki_data (list[dict]): Données scrappées sur Wikipedia, chaque entrée
            contenant au moins "id", "budget" et "revenue".

    Returns:
        list[dict]: Un dictionnaire par film, avec les champs fusionnés
            (id, title, tagline, director, casting, release, duration,
            budget, revenue, genres, synopsis, vote_average_tmdb,
            vote_count_tmdb, vote_average_ml, vote_count_ml).
    """
    top_movies = tmdb_data["movies"]
    # Index par id pour retrouver rapidement l'enrichissement Wikipedia d'un film
    enriched_by_id = {e["id"]: e for e in wiki_data}
    data = []

    for movie in top_movies:
        movie_id = movie["id"]
        ml_data = df.query("tmdbId == @movie_id")
        enriched = enriched_by_id.get(movie_id)

        result = {
            "id": movie.get("id"),
            "title": movie.get("title"),
            "tagline": movie.get("tagline"),
            "director": ", ".join(movie.get("directors", [])),
            "casting": ", ".join(movie.get("casting", [])),
            "release_date": movie.get("release_date"),
            "duration": movie.get("duration"),
            # TMDB en priorité ; "enriched" n'existe que pour les films dont le
            # budget/revenue était manquant côté TMDB (cf. raw_tmdb["missing"]
            # dans extract_web.py), on utilise alors la valeur Wikipedia
            "budget": enriched.get("budget") if enriched is not None else movie.get("budget"),
            "revenue": enriched.get("revenue") if enriched is not None else movie.get("revenue"),
            "genres": ", ".join(movie.get("genres", [])),
            "synopsis": movie.get("synopsis"),
            "vote_average_tmdb": movie.get("vote_average_tmdb"),
            "vote_count_tmdb": movie.get("vote_count_tmdb"),
            "vote_average_ml": ml_data["vote_average_ml"].iloc[0] if not ml_data.empty else None,
            "vote_count_ml": ml_data["vote_count_ml"].iloc[0] if not ml_data.empty else None
        }

        data.append(result)

    return data


def init_db():
    """Initialise la base de données SQLite en exécutant le script de schéma.

    Se connecte au fichier de base défini par DB et exécute le contenu du
    fichier SQL défini par SCHEMA (création des tables, etc.).
    """
    conn = sqlite3.connect(DB)
    with open(SCHEMA, "r") as f:
        conn.executescript(f.read())
    conn.close()

def load_to_db(data):
    """Insère les films dans la table "movies" de la base de données.

    Args:
        data (list[dict]): Films à insérer, au format produit par
            build_movie_dict (chaque clé du dictionnaire doit correspondre
            à un paramètre nommé de la requête SQL, ex. "release_date",
            "vote_average_tmdb").
    """
    conn = sqlite3.connect(DB)
    sql = """
        INSERT INTO movies VALUES (
            :id, :title, :tagline, :director, :casting,
            :release_date, :duration, :budget, :revenue, :genres,
            :synopsis, :vote_average_tmdb, :vote_count_tmdb,
            :vote_average_ml, :vote_count_ml
        )
    """
    for movie in data:
        conn.execute(sql, movie)
    conn.commit()
    conn.close()