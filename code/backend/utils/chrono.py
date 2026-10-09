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