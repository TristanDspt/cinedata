# src/main.py

"""
Point d'entrée du pipeline cinedata : orchestre l'extraction TMDB, MovieLens
et Wikipedia, fusionne les données (voir load_to_db.build_movie_dict) puis
exporte le résultat en CSV, prêt à être chargé en base de données.
"""

import pandas as pd

from extract_api import extract_tmdb
from extract_csv import load_movielens
from extract_web import enrich_from_wikipedia
from load_to_db import build_movie_dict, init_db, load_to_db
from precompute_recommendation import precompute

from config import CSV_TO_DB, SQL_RECOMMENDATION, DB_ENTRY, FORCE_REFRESH

# --------------------------------------------------------------------------------

def main(limit, force_refresh):
    """
    Exécute le pipeline complet : extraction (TMDB, MovieLens, Wikipedia), 
    fusion, chargement en base, puis précalcul du moteur de recommandation. 
    Chaque extraction réutilise son cache dans data/raw/ tant que force_refresh est False.
    """

    # Extract / Transform
    tmdb = extract_tmdb(limit=limit, force_refresh=force_refresh)
    movie_lens = load_movielens()
    tmdb_enriched = enrich_from_wikipedia(tmdb, force_refresh=force_refresh)

    # Aggregation / Load
    data = build_movie_dict(tmdb, movie_lens, tmdb_enriched)
    pd.DataFrame(data).to_csv(CSV_TO_DB, index=False)

    init_db()
    load_to_db(data)

    # Precalcul du moteur de recommandation
    precompute(SQL_RECOMMENDATION)


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    main(DB_ENTRY, FORCE_REFRESH)