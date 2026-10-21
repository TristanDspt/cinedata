# api/utils.py

def split_list(text: str | None) -> list[str]:
    """
    Transforme un texte "A, B, C" (colonne de la base) en liste ["A", "B", "C"].

    Renvoie une liste vide si le texte est None ou vide, et ignore les
    éléments vides et les espaces autour des noms.
    """
    if not text:
        return []
    return [item.strip() for item in text.split(",") if item.strip()]