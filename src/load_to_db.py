import extract_api as api
import extract_csv as csv


def build_movie_dict(df):
    popular_movies = api.get_popular_movie()

    movies = []

    for movie in popular_movies:
        details = api.get_movie_details(movie["id"])
        casting, directors = api.get_casting(movie["id"])

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
            #"genre_ids": movie.get("genre_ids"),
            "genres": [genre["name"] for genre in details.get("genres")],
            "synopsis": movie.get("overview"),
            "vote_average_tmdb": movie.get("vote_average"),
            "vote_count_tmdb": movie.get("vote_count"),
            "vote_average_ml": df.query("tmdbId == @movie_id")["rating_mean_ml"].iloc[0],
            "vote_count_ml": df.query("tmdbId == @movie_id")["rating_count_ml"].iloc[0]
        }
        
        movies.append(result)
        
    return movies