import os
import psycopg2
from psycopg2 import pool

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - compat environnement sans python-dotenv
    def load_dotenv(*args, **kwargs):
        return False

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "gt"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres")
}

DB_POOL_MIN = int(os.getenv("DB_POOL_MIN", "2"))
DB_POOL_MAX = int(os.getenv("DB_POOL_MAX", "20"))

_pool = None
_direct = set()   # connexions hors pool (repli), fermables directement


def _get_pool():
    global _pool
    if _pool is None:
        _pool = pool.ThreadedConnectionPool(DB_POOL_MIN, DB_POOL_MAX, **DB_CONFIG)
    return _pool


def get_connection():
    try:
        return _get_pool().getconn()
    except Exception:
        # Pool epuise ou indisponible : repli sur une connexion directe
        # pour ne jamais bloquer l'application.
        try:
            connexion = psycopg2.connect(**DB_CONFIG)
            _direct.add(connexion)
            return connexion
        except Exception as erreur:
            print(f"Erreur de connexion : {erreur}")
            return None


def close_connection(connexion):
    if connexion is None:
        return
    try:
        if not connexion.closed:
            connexion.rollback()
    except Exception:
        pass

    if connexion in _direct:
        _direct.discard(connexion)
        try:
            connexion.close()
        except Exception:
            pass
        return

    try:
        _get_pool().putconn(connexion)
    except Exception:
        try:
            connexion.close()
        except Exception:
            pass
