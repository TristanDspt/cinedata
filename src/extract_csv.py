"""extract_csv.py

Extraction et préparation des données MovieLens (fichiers CSV ratings/links)
en vue de leur fusion avec les données TMDB dans load_to_db.py.
"""

import pandas as pd

# --------------------------------------------------------------------------------

def load_movielens(config):
    """
    Charge et prépare les données MovieLens (ratings + links).

    Args:
        config (dict): Configuration chargée depuis config.yaml,
                       doit contenir config["path"]["ml_ratings"] et config["path"]["ml_links"].

    Returns:
        DataFrame: Colonnes tmdbId, vote_average_ml, vote_count_ml.
    """
    df_links = pd.read_csv(config["path"]["ml_links"])
    df_ratings = pd.read_csv(config["path"]["ml_ratings"])

    # Agrège les notes individuelles par film : moyenne et nombre de votes
    df_ratings = df_ratings.groupby(["movieId"]).agg({"rating": ["mean", "count"]}).reset_index().copy()
    df_ratings.columns = ["movieId", "vote_average_ml", "vote_count_ml"]
    # MovieLens note sur 5 ; on convertit sur 10 pour être comparable à vote_average_tmdb
    df_ratings["vote_average_ml"] = round(df_ratings["vote_average_ml"] * 2, 1)
    # Jointure avec ml_links pour récupérer le tmdbId (clé commune avec TMDB)
    df = df_ratings.merge(df_links, on="movieId", how="inner")
    df = df.drop(columns=["imdbId", "movieId"])

    return df