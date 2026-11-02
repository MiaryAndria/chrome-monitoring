import logging

from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.configuration import get_valeur_configuration
from backend.core.cache import cache_get, cache_set

logger = logging.getLogger(__name__)

_TTL_SECONDES = 60

# Cles dont l'absence en base a deja ete signalee (evite le spam de logs)
_cles_signalees = set()


def _signaler_absence(cle):
    if cle in _cles_signalees:
        return
    _cles_signalees.add(cle)
    logger.warning(
        "Configuration '%s' absente/non lisible en base : valeur par defaut utilisee.",
        cle,
    )


def get_configuration(cle, default=None):
    """Valeur (texte) de t_configuration pour une clé `type`, sinon `default`."""
    cache_key = f"config:{cle}"
    valeur_cache = cache_get(cache_key)
    if valeur_cache is not None:
        return valeur_cache

    connexion = get_connection()
    if connexion is None:
        _signaler_absence(cle)
        return default
    try:
        cur = connexion.cursor()
        row = get_valeur_configuration(cur, cle)
        if row and row[0] is not None:
            return cache_set(cache_key, row[0], _TTL_SECONDES)
        _signaler_absence(cle)
        return cache_set(cache_key, default, _TTL_SECONDES)
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
