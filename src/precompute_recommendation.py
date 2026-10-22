# src/precompute_recommendation.py

"""
Précalcul du moteur de recommandation par similarité de contenu.

Charge les films depuis la base SQLite (requête sql/recommendation.sql),
construit pour chaque film un texte ("soup") à partir de ses genres,
réalisateurs, casting, slogan et synopsis, le vectorise avec TF-IDF, puis
calcule la matrice de similarité cosinus entre tous les films.

Le résultat est sauvegardé sur disque (joblib) dans un artefact contenant :
    - "ids" : la liste des identifiants de films, dans l'ordre des lignes
    - "similarity" : la matrice de similarité (n_films x n_films)

L'API charge cet artefact une seule fois au démarrage et le consulte, sans
rien recalculer. À relancer après chaque rechargement de la base, sinon
l'API continue de servir des recommandations basées sur d'anciennes données.
"""

import sqlite3
import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import PROJECT_ROOT, DATABASE, SQL_DIR, ARTEFACT

# --------------------------------------------------------------------------------

def load_from_database(filename: str) -> pd.DataFrame:
    """
    Exécute un fichier .sql (dans sql/) sur la base et retourne le résultat
    sous forme de DataFrame.

    Args:
        filename: nom du fichier .sql, ex. "recommendation.sql"

    Returns:
        DataFrame avec une ligne par résultat de la requête.
    """
    with open(SQL_DIR / filename, "r", encoding="utf-8") as file:
        query = file.read()

    conn = sqlite3.connect(PROJECT_ROOT / DATABASE)
    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


def build_soup(df: pd.DataFrame, stick_cols: list, free_cols: list) -> pd.Series:
    """
    Construit le texte ("soup") de chaque film pour la vectorisation.

    Les colonnes "à entités" (genres, noms de personnes...) sont soudées :
    espaces et ponctuation sont supprimés, sauf la virgule qui sépare les
    éléments ("Tom Hanks, Tim Allen" devient "TomHanks,TimAllen"), pour que
    chaque entité reste un seul terme pour TF-IDF. Les colonnes de texte
    libre sont laissées telles quelles.

    Les valeurs manquantes (NaN) ne sont pas gérées : les colonnes doivent
    contenir du texte (chaîne vide acceptée).

    Args:
        df: DataFrame des films.
        stick_cols: colonnes à souder (ex. ["genres", "directors", "casting"]).
        free_cols: colonnes de texte libre (ex. ["tagline", "synopsis"]).

    Returns:
        Series : un texte par film, dans l'ordre du DataFrame.
    """
    glued = [df[col].str.replace(r"[^\w,]", "", regex=True) for col in stick_cols]
    free = [df[col] for col in free_cols]
    return pd.concat(glued + free, axis=1).agg(" ".join, axis=1)


def build_similarity(soup: pd.Series):
    """
    Calcule la matrice de similarité cosinus entre tous les films.

    Vectorise les textes avec TF-IDF (mots vides anglais ignorés), puis
    mesure la proximité de chaque paire de films : 0 = rien en commun,
    1 = identiques.

    Args:
        soup: un texte par film (résultat de build_soup).

    Returns:
        Matrice (n_films x n_films) : la valeur [i][j] est la similarité
        entre le film de la ligne i et celui de la ligne j.
    """
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(soup)
    return cosine_similarity(matrix)


def precompute(filename: str) -> None:
    """
    Calcule et sauvegarde l'artefact de recommandation.

    Charge les films, construit le soup, calcule la matrice de similarité,
    puis l'écrit avec la liste des identifiants dans le fichier ARTEFACT
    (le dossier est créé s'il n'existe pas). Écrase l'artefact précédent.

    Args:
        filename: fichier .sql d'extraction (dans sql/), ex. "recommendation.sql".
    """
    df = load_from_database(filename).reset_index(drop=True)
    df["soup"] = build_soup(df, ["genres", "directors", "casting"], ["tagline", "synopsis"])
    similarity = build_similarity(df["soup"])

    path = PROJECT_ROOT / ARTEFACT
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"ids": df["id"].tolist(), "similarity": similarity}, path)