import os
import time

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv(*args, **kwargs):
        return False

load_dotenv()

CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "60"))

_cache = {}


def cache_get(key):
    entree = _cache.get(key)
    if entree is None:
        return None

    valeur, expiration = entree
    if time.time() >= expiration:
        _cache.pop(key, None)
        return None

    return valeur


def cache_set(key, value, ttl=None):
    duree = CACHE_TTL_SECONDS if ttl is None else ttl
    _cache[key] = (value, time.time() + duree)
    return value


def cache_invalidate(key):
    _cache.pop(key, None)


def cache_invalidate_prefix(prefix):
    for key in list(_cache.keys()):
        if key.startswith(prefix):
            _cache.pop(key, None)


def cache_clear():
    _cache.clear()


__all__ = [
    "CACHE_TTL_SECONDS",
    "cache_get",
    "cache_set",
    "cache_invalidate",
    "cache_invalidate_prefix",
    "cache_clear",
]
