import time
from contextlib import contextmanager


@contextmanager
def chrono(label, etapes=None):
    """Affiche la durée et, si etapes est fourni, la cumule dans le dict."""
    t0 = time.perf_counter()
    try:
        yield
    finally:
        duree = time.perf_counter() - t0
        if etapes is not None:
            etapes[label] = round(etapes.get(label, 0) + duree, 3)
        print(f"[{label}] {duree:.2f}s")
        
def memo(fn):
    """Mémorise les résultats d'un get_or_create_* le temps d'une synchro."""
    cache = {}
    def wrapper(cur, *args):
        if args not in cache:
            cache[args] = fn(cur, *args)
        return cache[args]
    return wrapper


def _aware(dt):
    """Rend un datetime comparable (avec fuseau). Un datetime naïf est supposé en heure locale."""
    if dt is None:
        return None
    return dt.astimezone() if dt.tzinfo is None else dt