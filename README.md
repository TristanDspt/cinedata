# CinéData

Pipeline d'agrégation de données cinéma constitué dans le cadre du Bloc 1 du parcours Développeur IA (SIMPLON). Il collecte des données depuis trois sources hétérogènes, les fusionne et les charge dans une base SQLite exposable via une API REST.

## Sources de données

| Source | Type | Contenu |
|---|---|---|
| **TMDB API** | REST | Films, casting, genres, notes |
| **MovieLens** | CSV | Notes utilisateurs (25M ratings) |
| **Wikipedia** | Scraping | Budget et box-office manquants |

## Installation

    python -m venv cinedata_env
    cinedata_env\Scripts\activate
    pip install -r requirements.txt
    cp .env.example .env

Renseigner ensuite `TMDB_API_KEY` dans le fichier `.env` (clé gratuite sur [themoviedb.org](https://www.themoviedb.org/signup)).

## Utilisation

    python src/main.py

Les données brutes sont mises en cache dans `data/raw/` après la première exécution. Pour forcer une nouvelle extraction, supprimer les fichiers JSON ou passer `force_refresh=True` dans `main.py`.

## Architecture

    src/
      extract_api.py   # Extraction TMDB (top films, détails, casting)
      extract_csv.py   # Chargement et préparation MovieLens
      extract_web.py   # Scraping Wikipedia (budget/box-office)
      load_to_db.py    # Fusion des trois sources + insertion SQLite
      utils.py         # Fonctions partagées (requêtes HTTP, nettoyage)
      main.py          # Point d'entrée du pipeline
    data/
      raw/             # Données brutes extraites (cache JSON/CSV)
      processed/       # Export CSV final
      db/              # Base SQLite (non versionnée)
    sql/
      schema.sql       # Schéma de la base de données

## Compétences mobilisées

Bloc 1 du référentiel Dev IA — C1 à C5 : collecte, stockage et mise à disposition des données d'un projet IA.