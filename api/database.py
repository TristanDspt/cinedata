# api/database.py

from pathlib import Path
from config import SQL_DIR, DATABASE
import sqlite3

# --------------------------------------------------------------------------------

def execute_sql(filepath: Path, params=()) -> str:
    """
    Exécute le contenu d'un fichier .sql (dans sql/) avec les paramètres
    donnés, et retourne les résultats sous forme de liste de dicts.

    Paramètres :
        nom_fichier (str) : nom du fichier .sql, ex. "movies_list.sql"
        params (tuple) : valeurs pour les "?" du fichier SQL, dans l'ordre

    Retourne :
        list[dict] : une entrée par ligne de résultat
    """
    sql_file = SQL_DIR / filepath
    with open(sql_file, "r", encoding="utf-8") as file:
        sql_request = file.read()

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.execute(sql_request, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
