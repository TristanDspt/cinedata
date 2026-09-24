# utils.py

import requests
import time
import yaml

# --------------------------------------------------------------------------------

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

TIMEOUT = config["api_tmdb"]["timeout"]

# --------------------------------------------------------------------------------

def safe_get(url, retries=3, headers=None, timeout=TIMEOUT):
    """
    Effectue une requête GET sécurisée avec gestion des erreurs et retry sur 429.

    Args:
        url (str): URL de la requête.
        retries (int): Nombre de tentatives restantes en cas de 429. Défaut : 3.

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
        if err.response.status_code == 429:
            time_sleep = int(err.response.headers["Retry-After"]) + 1
            time.sleep(time_sleep)
            return safe_get(url, retries - 1, headers=headers, timeout=timeout)
        else:
            print(f"HTTP error : {err}")
    except requests.exceptions.RequestException as err:
        print(f"Unknown error : {err}")
    return None