# web_extract.py

import os
from bs4 import BeautifulSoup
import yaml
import json

from utils import safe_get

# --------------------------------------------------------------------------------

BASE_DIR = os.path.dirname(__file__)
config_path = os.path.join(BASE_DIR, "config.yaml")

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

BASE_URL = config["wikipedia"]["base_url"]
WIKI_RAW = config["path"]["raw_wiki"]

# --------------------------------------------------------------------------------

def get_wikipedia_url(title, release_date):
    release_year = release_date[:4]
    clean_title = title.replace(" ", "+")

    url = f"{BASE_URL}/w/index.php?search=movie+{clean_title}+{release_year}&title=Special:Search"
    
    return url


def scrape_wikipedia(title, release_date):
    search_url = get_wikipedia_url(title, release_date)
    headers = {"User-Agent": "CineDataBot/1.0 (educational project; student@cinedata.edu)"}
    response = safe_get(search_url, headers=headers)

    if response is None:
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    element = soup.find("a", {"data-serp-pos": "0"})

    if element:
        film_url = element["href"].split("?")[0]
        if film_url.startswith("/"):
            film_url = BASE_URL + film_url
    else:
        print(f"No URL find for {title}")
        return None

    return film_url


def scrape_infobox(film_url):
    response = safe_get(film_url)
    result = {"budget": None, "revenue": None}

    if response is None:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    th_budget = soup.find("th", string="Budget")
    th_revenue = soup.find("th", string="Box office")

    if th_budget:
        td = th_budget.parent.find("td")
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
                print(f"No URL for {title}")
                continue

            result = scrape_infobox(url)
            if result is None:
                print(f"No scrape for {title}")
                continue

            enriched = {
                "id": movie.get("id"),
                "budget": result.get("budget"),
                "revenue": result.get("revenue"),
            }

            enriched_from_wiki.append(enriched)

        with open(WIKI_RAW, "w") as f:
            json.dump(enriched_from_wiki, f)

    return enriched_from_wiki