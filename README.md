# CinéData

Pipeline d'agrégation de données cinéma constitué dans le cadre du Bloc 1 du parcours Développeur IA (SIMPLON). Il collecte des données depuis trois sources hétérogènes, les fusionne, les charge dans une base SQLite, puis les expose via une API REST (FastAPI) avec un moteur de recommandation de films par similarité de contenu.

## Sources de données

| Source | Type | Contenu |
|---|---|---|
| **TMDB API** | REST | Films les mieux notés (> 2000 votes), détails, casting, réalisateurs, genres, notes |
| **MovieLens** | CSV | Notes utilisateurs (~100 000 notes, jeu `ml-latest-small`) |
| **Wikipedia** | Scraping | Budget et box-office quand TMDB ne les fournit pas de façon fiable |

## Installation

    python -m venv cinedata_env
    cinedata_env\Scripts\activate
    pip install -r requirements.txt
    cp .env.example .env

Renseigner ensuite `TMDB_API_KEY` dans le fichier `.env` avec votre **jeton d'accès en lecture** TMDB (API Read Access Token), gratuit sur [themoviedb.org](https://www.themoviedb.org/signup).

## Utilisation

**1. Lancer le pipeline** (extraction, fusion, chargement en base, précalcul du moteur de recommandation) :

    python src/main.py

Les données brutes sont mises en cache dans `data/raw/` après la première exécution. Pour forcer une nouvelle extraction, passer `force_refresh: true` dans `config.yaml` ou supprimer les fichiers JSON.

**2. Lancer l'API**, depuis la racine du projet :

    uvicorn main:app --reload --app-dir api

Documentation interactive (Swagger) : http://127.0.0.1:8000/docs

> L'API charge le moteur de recommandation au démarrage. Après chaque exécution du pipeline, **redémarrer l'API** pour qu'elle prenne en compte l'artefact mis à jour.

## Endpoints

| Route | Description |
|---|---|
| `GET /info` | Informations sur l'API |
| `GET /health` | État de l'API (vérifie l'accès à la base) |
| `GET /movies/?page=1` | Liste paginée des films (10 par page) |
| `GET /movies/{movie_id}` | Détail complet d'un film (404 si inconnu) |
| `GET /recommendation/{movie_id}` | Films les plus proches d'un film donné, avec leur score (404 si inconnu) |

## Moteur de recommandation

Recommandation **par similarité de contenu** (sans LLM) :

1. Pour chaque film, un texte est construit à partir des genres, réalisateurs, casting, slogan et synopsis. Les genres et les noms propres sont « soudés » (`Tom Hanks` devient `TomHanks`) pour rester un seul terme.
2. Les textes sont vectorisés avec **TF-IDF**, puis la **similarité cosinus** est calculée entre tous les films.
3. Ce calcul est fait **une fois**, à chaque exécution du pipeline, et sauvegardé sur disque (`data/models/recommendation.joblib`, non versionné) : la liste des identifiants et la matrice de similarité.
4. L'API charge cet artefact au démarrage et se contente de le consulter. Les détails des films recommandés sont lus dans la base.

**Limite connue :** la similarité est *lexicale* (elle compare les mots, pas le sens). Deux synopsis qui partagent un mot comme « princess » peuvent se rapprocher sans rapport réel. Le `score` renvoyé sert d'indicateur de confiance.

## Flux du projet

![Flux du projet CinéData](docs/flux.svg)

Wikipedia et MovieLens enrichissent les films issus de TMDB, qui reste la source principale. Le résultat fusionné est chargé en SQLite, puis le précalcul TF-IDF produit `recommendation.joblib`. L'API lit la base pour `/movies` et le joblib pour `/recommendation`.

## Architecture

    config.yaml            # Configuration centrale (chemins, paramètres, API TMDB)
    src/
      main.py              # Point d'entrée du pipeline
      config.py            # Lecture de config.yaml, chemins absolus
      extract_api.py       # Extraction TMDB (top films, détails, casting)
      extract_csv.py       # Chargement et préparation MovieLens
      extract_web.py       # Scraping Wikipedia (budget/box-office)
      load_to_db.py        # Fusion des trois sources + insertion SQLite
      precompute_recommendation.py  # Précalcul du moteur de recommandation
      utils.py             # Fonctions partagées (requêtes HTTP, nettoyage)
    api/
      main.py              # Application FastAPI
      config.py            # Configuration de l'API
      database.py          # Exécution des requêtes SQL
      schemas.py           # Modèles Pydantic (entrées/sorties)
      reco_engine.py       # Chargement de l'artefact et consultation
      utils.py             # Fonctions utilitaires
      routers/             # system, movies, recommendation
    sql/
      schema.sql           # Schéma de la base de données
      recommendation.sql   # Extraction pour le moteur de recommandation
      api/                 # Requêtes de l'API (paramétrées)
    data/
      raw/                 # Données brutes extraites (cache JSON/CSV)
      processed/           # Export CSV final
      db/                  # Base SQLite (non versionnée)
      models/              # Artefact de recommandation (non versionné)

## Pistes d'amélioration

- **Recommandation enrichie par un LLM** (étape suivante prévue) : le moteur de similarité continue de choisir les films, et un LLM (Mistral) rédige une recommandation argumentée à partir de cette liste, via une route dédiée. Si le service est indisponible, l'API renvoie une erreur 503 explicite et `/recommendation/{movie_id}` continue de fonctionner
- Pondérer les catégories (genres, casting, synopsis) dans la similarité, et filtrer les recommandations sous un seuil de score
- Passer à une similarité sémantique (embeddings) pour dépasser la limite lexicale
- Filtres genre/année sur `/movies/` et endpoints de classements
- Schéma relationnel normalisé (genres, personnes, tables d'association) à la place des colonnes texte

## Compétences mobilisées

Bloc 1 du référentiel Dev IA — C1 à C5 : collecte, stockage et mise à disposition des données d'un projet IA.