# load_to_db.py

import os
import yaml
import json
import pandas as pd

from extract_csv import load_movielens

# --------------------------------------------------------------------------------

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

TMDB_RAW = config["path"]["raw_tmdb"]
WIKI_RAW = config["path"]["raw_wiki"]

# --------------------------------------------------------------------------------

def build_movie_dict(tmdb_data, df, wiki_data):
    top_movies = tmdb_data["movies"]
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
            "director": movie.get("directors"),
            "casting": movie.get("casting"),
            "release": movie.get("release_date"),
            "duration": movie.get("duration"),
            "budget": enriched.get("budget") if enriched is not None else movie.get("budget"),
            "revenue": enriched.get("revenue") if enriched is not None else movie.get("revenue"),
            "genres": movie.get("genres"),
            "synopsis": movie.get("synopsis"),
            "vote_average_tmdb": movie.get("vote_average_tmdb"),
            "vote_count_tmdb": movie.get("vote_count_tmdb"),
            "vote_average_ml": ml_data["vote_average_ml"].iloc[0] if not ml_data.empty else None,
            "vote_count_ml": ml_data["vote_count_ml"].iloc[0] if not ml_data.empty else None
        }
        
        data.append(result)
        
    return data
