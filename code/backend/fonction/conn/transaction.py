from contextlib import contextmanager

from backend.fonction.conn.connexion import get_connection, close_connection


@contextmanager
def lecture():
    """Bloc de lecture : ouvre un curseur en lecture seule.

    PostgreSQL refuse toute écriture tant que ce contexte est actif : un
    ``insert_*`` glissé par erreur dans une fonction de lecture lève une erreur
    au lieu d'être silencieusement annulé par le rollback final.

    Si la base est injoignable, le curseur vaut ``None`` et le service garde son
    comportement de repli (``if cur is None: return ...``).
    """
    connexion = get_connection()
    if connexion is None:
        yield None
        return

    cur = None
    try:
        try:
            connexion.set_session(readonly=True)
        except Exception:
            pass
        cur = connexion.cursor()
        yield cur
    finally:
        if cur is not None:
            try:
                cur.close()
            except Exception:
                pass
        try:
            connexion.rollback()
        except Exception:
            pass
        try:
            connexion.set_session(readonly=False)
        except Exception:
            pass
        close_connection(connexion)


@contextmanager
def transaction():
    """Bloc d'écriture : une seule transaction, commit si tout réussit.

    Toutes les écritures du bloc sont validées ensemble ou annulées ensemble,
    ce qui permet au service d'enchaîner plusieurs opérations du repository sans
    exposer d'état intermédiaire en base.
    """
    connexion = get_connection()
    if connexion is None:
        yield None
        return

    cur = None
    try:
        cur = connexion.cursor()
        yield cur
        connexion.commit()
    except Exception:
        try:
            connexion.rollback()
        except Exception:
            pass
        raise
    finally:
        if cur is not None:
            try:
                cur.close()
            except Exception:
                pass
        close_connection(connexion)


__all__ = ["lecture", "transaction"]
