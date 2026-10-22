# api/reco_engine.py

"""
Moteur de recommandation côté API : charge l'artefact précalculé par
src/precompute_recommendation.py (une seule fois, au démarrage de l'API)
et expose recommend() pour le consulter, sans aucun recalcul.

L'API doit être redémarrée après chaque exécution du pipeline pour prendre
en compte un nouvel artefact.
"""

import joblib

from config import PROJECT_ROOT, ARTEFACT, TOP_N

# --------------------------------------------------------------------------------

_artefact = joblib.load(PROJECT_ROOT / ARTEFACT)

IDS = _artefact["ids"]
SIMILARITY = _artefact["similarity"]
POSITION = {movie_id: pos for pos, movie_id in enumerate(IDS)}


def recommend(movie_id: int, top_n: int = TOP_N) -> list[tuple[int, float]] | None:
    """
    Retourne les films les plus proches d'un film donné.

    Args:
        movie_id: identifiant du film (celui de la base).
        top_n: nombre de films à retourner. Défaut : TOP_N (config.yaml).

    Returns:
        Liste de tuples (id du film recommandé, score de similarité), du plus
        proche au moins proche, le film demandé étant exclu. None si
        l'identifiant est inconnu.
    """
    pos = POSITION.get(movie_id)
    if pos is None:
        return None

    best = SIMILARITY[pos].argsort()[::-1][1 : top_n + 1]
    return [(IDS[i], float(SIMILARITY[pos][i])) for i in best]