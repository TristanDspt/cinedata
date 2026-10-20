-- Liste paginée des films : id, titre, année de sortie
SELECT id, title, release_date
FROM movies
ORDER BY id
LIMIT ?
OFFSET ?;