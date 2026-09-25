# main

import pandas as pd
import yaml

from extract_api import extract_tmdb
from extract_csv import load_movielens
from extract_web import enrich_from_wikipedia
from load_to_db import build_movie_dict

# --------------------------------------------------------------------------------

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

EXPORT_TO_DB = config["path"]["export"]

# --------------------------------------------------------------------------------

if __name__ == "__main__":

    tmdb = extract_tmdb(limit=100, force_refresh=False)
    movie_lens = load_movielens(config)
    tmdb_enriched = enrich_from_wikipedia(tmdb, force_refresh=False)

    data = build_movie_dict(tmdb, movie_lens, tmdb_enriched)

    pd.DataFrame(data).to_csv(EXPORT_TO_DB, index=False)
