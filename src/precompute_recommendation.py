# src/precompute_recommendation.py

import os
import sqlite3
import joblib
import pandas as pd

from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import PROJECT_ROOT, DATABASE, SQL_DIR

# --------------------------------------------------------------------------------

def load_from_database(filename: str) -> pd.DataFrame:
    """
    Exécute le contenu d'un fichier .sql (dans sql/) avec les paramètres
    donnés, et retourne les résultats sous forme de liste de dicts.

    Paramètres :
        nom_fichier (str) : nom du fichier .sql, ex. "recommendation.sql"

    Retourne :
        DataFrame : une entrée par ligne de résultat
    """
    sql_file = SQL_DIR / filename
    with open(sql_file, "r", encoding="utf-8") as file:
        sql_request = file.read()

    conn = sqlite3.connect(PROJECT_ROOT / DATABASE)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.execute(sql_request)
        rows = cursor.fetchall()
        return pd.DataFrame([dict(row) for row in rows])
    finally:
        conn.close()