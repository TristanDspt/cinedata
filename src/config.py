# scr/config.py

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

# --------------------------------------------------------------------------------

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")


def find_project_root() -> Path:
    """
    Recherche la racine du projet à partir de l'emplacement
    du fichier courant.

    La fonction remonte l'arborescence des dossiers jusqu'à
    trouver un fichier requirements.txt, considéré comme le
    point d'ancrage du projet.

    Returns:
        Chemin absolu vers la racine du projet.

    Raises:
        FileNotFoundError: Si aucun fichier requirements.txt
            n'est trouvé dans l'arborescence parente.
    """
    current = Path(__file__).resolve()

    while current != current.parent:
        if (current / "requirements.txt").exists():
            return current
        current = current.parent

    raise FileNotFoundError("requirements.txt introuvable")

PROJECT_ROOT = find_project_root()
SQL_DIR = PROJECT_ROOT / "sql"


def load_yaml(filepath: Path) -> dict:
    """
    Charge et retourne le contenu d'un fichier YAML.

    Args:
        filepath: Chemin du fichier YAML.

    Returns:
        Dictionnaire contenant les données du fichier.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

config = load_yaml(PROJECT_ROOT / "config.yaml")

# config.py
TIMEOUT = config["api_tmdb"]["timeout"]

# extract_api.py
BASE_TMDB_URL = config["api_tmdb"]["base_url"]
TMDB_RAW = PROJECT_ROOT / config["path"]["raw_tmdb"]

# extract_csv.py (voir plus bas)
ML_RATINGS = PROJECT_ROOT / config["path"]["ml_ratings"]
ML_LINKS = PROJECT_ROOT / config["path"]["ml_links"]

# extract_web.py
BASE_WIKI_URL = config["wikipedia"]["base_url"]
WIKI_RAW = PROJECT_ROOT / config["path"]["raw_wiki"]
WIKI_HEADERS = {"User-Agent": "CineDataBot/1.0 (educational project; student@cinedata.edu)"}

# load_to_db.py
MIN_RELIABLE = config["data_quality"]["min_reliable"]
SCHEMA = PROJECT_ROOT / config["database"]["schema"]
DATABASE = PROJECT_ROOT / config["database"]["db_file"]

# precompute_recommendation.py
SQL_RECOMMENDATION = config["recommendation"]["sql_file"]
ARTEFACT = PROJECT_ROOT / config["recommendation"]["artefact_path"]

# main.py
CSV_TO_DB = PROJECT_ROOT / config["path"]["export"]
DB_ENTRY = config["pipeline"]["db_entry"]
FORCE_REFRESH = config["pipeline"]["force_refresh"]