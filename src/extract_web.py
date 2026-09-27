"""web_extract.py

Enrichissement des films depuis Wikipedia : pour les films dont TMDB n'a pas
fourni de budget/revenu fiable (voir extract_api.py, clé "missing"), on
recherche la page Wikipedia correspondante et on en extrait ces valeurs
depuis l'infobox, avant sauvegarde en JSON (data/raw/wiki.json).
"""

import os
from bs4 import BeautifulSoup
import yaml
import json

from utils import safe_get, clean_wiki_value

# --------------------------------------------------------------------------------

BASE_DIR = os.path.dirname(__file__)
config_path = os.path.join(BASE_DIR, "config.yaml")

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

BASE_URL = config["wikipedia"]["base_url"]
WIKI_RAW = config["path"]["raw_wiki"]

WIKI_HEADERS = {"User-Agent": "CineDataBot/1.0 (educational project; student@cinedata.edu)"}

# --------------------------------------------------------------------------------

def get_wikipedia_url(title, release_date):
    """
    Construit l'URL de recherche Wikipedia pour un film donné.

    Args:
        title (str): Titre du film.
        release_date (str): Date de sortie au format "YYYY-MM-DD" (seule
            l'année est utilisée pour affiner la recherche).

    Returns:
        str: URL de la page de résultats de recherche Wikipedia.
    """
    release_year = release_date[:4]
    clean_title = title.replace(" ", "+")

    url = f"{BASE_URL}/w/index.php?search=movie+{clean_title}+{release_year}&title=Special:Search"

    return url


def scrape_wikipedia(title, release_date):
    """
    Recherche un film sur Wikipedia et retourne l'URL de sa page.

    Prend le premier résultat de la recherche (data-serp-pos="0"), sans
    garantie que ce soit la bonne page si le titre est ambigu.

    Args:
        title (str): Titre du film.
        release_date (str): Date de sortie au format "YYYY-MM-DD".

    Returns:
        str: URL absolue de la page Wikipedia du film, ou None si la
            requête échoue ou si aucun résultat n'est trouvé.
    """
    search_url = get_wikipedia_url(title, release_date)
    response = safe_get(search_url, headers=WIKI_HEADERS)

    if response is None:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    element = soup.find("a", {"data-serp-pos": "0"})

    if element:
        film_url = element["href"].split("?")[0]
        if film_url.startswith("/"):
            film_url = BASE_URL + film_url
    else:
        print(f"Unable to generate a URL for {title}")
        return None

    return film_url


def scrape_infobox(film_url):
    """
    Extrait le budget et le box-office depuis l'infobox d'une page Wikipedia.

    Args:
        film_url (str): URL de la page Wikipedia du film.

    Returns:
        dict: {"budget": str|None, "revenue": str|None}, ou None si la
            requête échoue. Les valeurs sont du texte brut (non normalisé),
            à nettoyer ensuite via clean_wiki_value.
    """
    response = safe_get(film_url, headers=WIKI_HEADERS)
    result = {"budget": None, "revenue": None}

    if response is None:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    th_budget = soup.find("th", string="Budget")
    th_revenue = soup.find("th", string="Box office")

    if th_budget:
        td = th_budget.parent.find("td")
        # Les <sup> contiennent des appels de note (ex. "[1]") à retirer
        for sup in td.find_all("sup"):
            sup.decompose()
        result["budget"] = td.text
    if th_revenue:
        td = th_revenue.parent.find("td")
        for sup in td.find_all("sup"):
            sup.decompose()
        result["revenue"] = td.text

    return result

# --------------------------------------------------------------------------------

def enrich_from_wikipedia(raw_tmdb, force_refresh=False):
    """
    Complète le budget/revenu des films marqués "missing" par TMDB via Wikipedia.

    Réutilise le fichier WIKI_RAW s'il existe déjà (sauf si force_refresh=True),
    pour éviter de re-scraper Wikipedia à chaque exécution.

    Args:
        raw_tmdb (dict): Données brutes TMDB, doit contenir la clé "missing"
            (liste de films avec id, title, release_date).
        force_refresh (bool): Si True, ignore le cache et relance le scraping.
            Défaut : False.

    Returns:
        list[dict]: Un dict par film enrichi, avec "id", "budget" et "revenue"
            (valeurs nettoyées via clean_wiki_value, potentiellement None).
    """
    if os.path.exists(WIKI_RAW) and not force_refresh:
        with open(WIKI_RAW, "r") as f:
            enriched_from_wiki = json.load(f)
    else:
        enriched_from_wiki = []
        missing = raw_tmdb["missing"]

        for movie in missing:
            title = movie.get("title")
            release_date = movie.get("release_date")

            url = scrape_wikipedia(title, release_date)
            if url is None:
                print(f"No URL find for {title}")
                continue

            result = scrape_infobox(url)
            if result is None:
                print(f"Unable to scrappe for {title}")
                continue

            budget = clean_wiki_value(result.get("budget"))
            if budget is None:
                print(f"{title} — budget ignored : unusable value")
            revenue = clean_wiki_value(result.get("revenue"))
            if revenue is None:
                print(f"{title} — revenue ignored : unusable value")

            enriched = {
                "id": movie.get("id"),
                "budget": budget,
                "revenue": revenue,
            }

            enriched_from_wiki.append(enriched)

        with open(WIKI_RAW, "w") as f:
            json.dump(enriched_from_wiki, f)

    return enriched_from_wiki