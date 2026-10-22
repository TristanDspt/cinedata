# src/precompute_recommendation.py

import os
import sqlite3
import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import PROJECT_ROOT, DATABASE, SQL_DIR

# --------------------------------------------------------------------------------

def load_from_database(filename: str) -> pd.DataFrame:
    """
    Exécute un fichier .sql (dans sql/) sur la base et retourne le résultat
    sous forme de DataFrame.

    Args:
        filename: nom du fichier .sql, ex. "recommendation.sql"
    """
    with open(SQL_DIR / filename, "r", encoding="utf-8") as file:
        query = file.read()

    conn = sqlite3.connect(PROJECT_ROOT / DATABASE)
    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()