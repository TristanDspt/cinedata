# src/utils.py

"""
Fonctions utilitaires partagées par les modules d'extraction (extract_api,
extract_web) : requêtes HTTP robustes (retry, timeout) et nettoyage des
valeurs monétaires scrappées sur Wikipedia.
"""

import requests
import time
from config import TIMEOUT

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


def clean_wiki_value(value: str) -> int:
    """
    Normalise une valeur monétaire brute extraite d'une infobox Wikipedia.

    Ne traite que les montants en dollars (préfixés par "$"). Formats gérés :
    "$X", "$X thousand", "$X million", "$X billion" (casse indifférente),
    avec ou sans séparateur de milliers (ex. "$250,000", "$1.5 million").

    Une valeur absente ou sans "$" (autre devise, texte libre) est ignorée
    silencieusement. Une valeur avec "$" mais illisible (fourchette comme
    "$10–15 million", unité inconnue comme "$5 bananas", montant manquant...)
    est ignorée aussi, mais un message est affiché pour pouvoir la repérer.

    Args:
        value (str | None): Texte brut de l'infobox (ex. "$1.5 million",
            "$250,000").

    Returns:
        int | None: Montant en dollars, ou None si la valeur est absente,
            n'est pas exprimée en dollars ou n'a pas pu être interprétée.
    """
    raw_value = value

    if value is None:
        return None
    if "$" not in value:
        print(f"No $ sign in value : {raw_value}")
        return None

    # \u00a0 : espace ins\écable parfois utilis\ée par Wikipedia entre le chiffre
    # et l'unit\é (ex. "million")
    value = value.replace("US$", "").replace("$", "").replace("\u00a0", " ").replace(",", "")
    value = value.strip().split()

    conversion = {
        "thousand": 1_000,
        "million": 1_000_000,
        "billion": 1_000_000_000
    }

    try:
        if len(value) > 1 and value[1].lower() in conversion:
            return int(round(float(value[0]) * conversion[value[1].lower()], 0))
        elif len(value) > 1 and value[1].lower() not in conversion:
            print(f"Unknown word in value : {raw_value}")
            return None
        return int(value[0])
    
    except Exception as e:
        print(f"{raw_value} | {type(e).__name__} : {e}")
        return None

if __name__ == "__main__":
    print(clean_wiki_value("$16.4 million"))
    print(clean_wiki_value("$250 thousand"))
