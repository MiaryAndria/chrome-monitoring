from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.configuration import get_valeur_configuration
from backend.core.cache import cache_get, cache_set

_TTL_SECONDES = 60


def get_configuration(cle, default=None):
    """Valeur (texte) de t_configuration pour une clé `type`, sinon `default`."""
    cache_key = f"config:{cle}"
    valeur_cache = cache_get(cache_key)
    if valeur_cache is not None:
        return valeur_cache

    connexion = get_connection()
    if connexion is None:
        return default
    try:
        cur = connexion.cursor()
        row = get_valeur_configuration(cur, cle)
        valeur = row[0] if row and row[0] is not None else default
        return cache_set(cache_key, valeur, _TTL_SECONDES)
    finally:
        close_connection(connexion)


def get_int_configuration(cle, default):
    valeur = get_configuration(cle)
    try:
        return int(valeur)
    except (TypeError, ValueError):
        return int(default)


def get_float_configuration(cle, default):
    valeur = get_configuration(cle)
    try:
        return float(valeur)
    except (TypeError, ValueError):
        return float(default)


def get_list_configuration(cle, default):
    """Valeur CSV (ex. 'USB_ADDED,USB_REMOVED') -> liste nettoyée."""
    valeur = get_configuration(cle)
    if valeur is None:
        return list(default)
    return [item.strip() for item in str(valeur).split(",") if item.strip()]
