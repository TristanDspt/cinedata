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

from config import EXPORT_TO_DB

# --------------------------------------------------------------------------------

def main(limit, force_refresh):
    # Chaque étape réutilise son cache JSON/CSV existant (force_refresh=False)
    # tant que les fichiers dans data/raw/ ne sont pas supprimés
    tmdb = extract_tmdb(limit=limit, force_refresh=force_refresh)
    movie_lens = load_movielens()
    tmdb_enriched = enrich_from_wikipedia(tmdb, force_refresh=force_refresh)

    data = build_movie_dict(tmdb, movie_lens, tmdb_enriched)

    pd.DataFrame(data).to_csv(EXPORT_TO_DB, index=False)

    init_db()
    load_to_db(data)

# --------------------------------------------------------------------------------

if __name__ == "__main__":
    main(1000, True)