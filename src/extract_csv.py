import pandas as pd

df_links = pd.read_csv(r"..\data\raw\movie_lens\links.csv")
df_ratings = pd.read_csv(r"..\data\raw\movie_lens\ratings.csv")

df_ratings = df_ratings.groupby(["movieId"]).agg({"rating": ["mean", "count"]}).reset_index().copy()
df_ratings.columns = ["movieId", "vote_average_ml", "vote_count_ml"]
df = df_ratings.merge(df_links, on='movieId', how='inner')
df = df.drop(columns=['imdbId', 'movieId'])