"""utils.py

Fonctions utilitaires partagées par les modules d'extraction (extract_api,
extract_web) : requêtes HTTP robustes (retry, timeout) et nettoyage des
valeurs monétaires scrappées sur Wikipedia.
"""

import os
import requests
import time
import yaml

# --------------------------------------------------------------------------------

BASE_DIR = os.path.dirname(__file__)
config_path = os.path.join(BASE_DIR, "config.yaml")

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

TIMEOUT = config["api_tmdb"]["timeout"]

# --------------------------------------------------------------------------------

def safe_get(url, retries=3, headers=None, timeout=TIMEOUT):
    """
    Effectue une requête GET sécurisée avec gestion des erreurs et retry sur 429.

    Args:
        url (str): URL de la requête.
        retries (int): Nombre de tentatives restantes en cas de 429. Défaut : 3.
        headers (dict): En-têtes HTTP à envoyer (ex. User-Agent, Authorization).
        timeout (int): Délai max en secondes avant abandon. Défaut : TIMEOUT (config).

    Returns:
        Response: Objet response requests, ou None en cas d'erreur.
    """
    if retries == 0:
        print("Too much tentatives, try again later")
        return None
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.ConnectionError:
        print("Connexion error.")
    except requests.exceptions.Timeout:
        print("Timeout.")
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 403:
            # Accès refusé : pas de retry possible, on laisse le bloc suivant
            # logguer l'erreur et retourner None
            pass
        elif err.response.status_code == 429:
            # Trop de requêtes : on attend la durée indiquée par l'API puis on
            # retente (en consommant une tentative), respectant Retry-After
            time_sleep = int(err.response.headers["Retry-After"]) + 1
            time.sleep(time_sleep)
            return safe_get(url, retries - 1, headers=headers, timeout=timeout)
        else:
            print(f"HTTP error : {err}")
    except requests.exceptions.RequestException as err:
        print(f"Unknown error : {err}")
    return None


def clean_wiki_value(value):
    """
    Normalise une valeur monétaire brute extraite d'une infobox Wikipedia.

    Ne traite que les montants en dollars (préfixés par "$") ; toute autre
    valeur (absente, dans une autre devise, format inattendu...) est ignorée.

    Attention : les nombres avec séparateur de milliers (virgule, ex.
    "$120,000,000") ne sont pas gérés et provoqueront une ValueError sur
    float(). Seuls les formats "$X" et "$X million" sont supportés.

    Args:
        value (str): Texte brut de l'infobox (ex. "$1.5 million", "$500000").

    Returns:
        float: Montant en dollars, ou None si la valeur est absente ou
            n'est pas exprimée en dollars.
    """
    if value is None:
        return None
    if "$" not in value:
        return None

    # \u00a0 : espace ins\écable parfois utilis\ée par Wikipedia entre le chiffre
    # et l'unit\é (ex. "million")
    value = value.replace("$", "").replace("\u00a0", " ")
    value = value.strip().split()

    if len(value) > 1 and value[1] == "million":
        return float(value[0]) * 1_000_000

    return float(value[0])