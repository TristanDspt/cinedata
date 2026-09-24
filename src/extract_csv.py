# extract_csv.py

import pandas as pd
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def load_movielens(config):
    """
    Charge et prépare les données MovieLens (ratings + links).

    Args:
        config (dict): Configuration chargée depuis config.yaml,
                       doit contenir config["paths"]["ratings"] et config["paths"]["links"].

    Returns:
        DataFrame: Colonnes tmdbId, vote_average_ml, vote_count_ml.
    """
    df_links = pd.read_csv(config["paths"]["links"])
    df_ratings = pd.read_csv(config["paths"]["ratings"])

    df_ratings = df_ratings.groupby(["movieId"]).agg({"rating": ["mean", "count"]}).reset_index().copy()
    df_ratings.columns = ["movieId", "vote_average_ml", "vote_count_ml"]
    df = df_ratings.merge(df_links, on="movieId", how="inner")
    df = df.drop(columns=["imdbId", "movieId"])

    return df