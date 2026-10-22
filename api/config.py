# api/config.py

from pathlib import Path
import yaml

# --------------------------------------------------------------------------------

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
SQL_DIR = PROJECT_ROOT / "sql" / "api"


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
DATABASE = config["database"]["db_file"]
