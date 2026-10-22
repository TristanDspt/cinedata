-- extraction depuis la base pour l'algorythme de recommandation

SELECT
	id,
	title,
	tagline,
	directors,
	casting,
	release_date,
	duration,
	budget,
	genres,
	synopsis,
	vote_average_tmdb,
	vote_count_tmdb,
	vote_average_ml,
	vote_count_ml
FROM 
	movies