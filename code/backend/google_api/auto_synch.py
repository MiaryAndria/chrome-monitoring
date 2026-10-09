import logging
import threading
from datetime import datetime, timedelta, timezone
import time
# from backend.utils.save_to_json import save_to_json
from backend.utils.chrono import chrono

from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.statut import get_or_create_statut
from backend.fonction.metier.service.import_service import synchroniser_tout
from backend.fonction.metier.repository.synchronisation import (
    get_derniere_fenetre_fin_by_source,
    insert_synchronisation_historique,
    insert_synchronisation_statut,
    update_synchronisation_resultat,
)

logger = logging.getLogger(__name__)
TZ_LOCAL = timezone(timedelta(hours=3))
INTERVALLE_SECONDES = 1* 60        # une synchro toutes les 1
MARGE_72h = timedelta(hours=72)           # chevauchement pour les événements tardifs
PREMIERE_SYNCHRO = timedelta(days=90)
MARGE_1h = timedelta(hours=1)

_verrou = threading.Lock()           # empêche deux synchros en même temps
_arret = threading.Event()           # pour arrêter proprement la boucle
_thread = None

# def _sauver_suivi(suivi):
#     """Écrit le suivi en JSON (output/synchro_<id>_<timestamp>.json) sans jamais faire planter la synchro."""
#     try:
#         save_to_json(suivi, f"synchro_{suivi.get('id_sync') or 'sans_id'}")
#     except Exception:
#         logger.exception("Impossible d'écrire le suivi JSON")
        
def _changer_statut(conn, cur, id_sync, nom_statut):
    id_statut = get_or_create_statut(cur, nom_statut)
    insert_synchronisation_statut(cur, id_statut, id_sync, datetime.now(timezone.utc))
    conn.commit()


# def executer_synchronisation():
#     if not _verrou.acquire(blocking=False):
#         logger.warning("Synchronisation déjà en cours, ce tour est ignoré")
#         return False
    
#     conn = None
#     cur = None
#     id_sync = None
#     try:
#         conn = get_connection()
#         cur = conn.cursor()
#         # source = "google"
#         # today = datetime.now(timezone.utc)
#         # lancement = datetime.now(timezone.utc)
#         source = "google"
#         lancement = datetime.now(timezone.utc)     # heure réelle = fin de la fenêtre

#         dernier = get_derniere_fenetre_fin_by_source(cur, source)

#         if dernier is None:
#             fenetre_debut = lancement - PREMIERE_SYNCHRO
#         else:
#             deja_fait_aujourdhui = (
#                 dernier.astimezone(TZ_LOCAL).date() == lancement.astimezone(TZ_LOCAL).date()
#             )
#             marge = MARGE_1h if deja_fait_aujourdhui else MARGE_72h
#             fenetre_debut = dernier - marge

#         fenetre_fin = lancement

#         id_sync = insert_synchronisation_historique(
#             cur, source, lancement, fenetre_debut, fenetre_fin
#         )
#         _changer_statut(conn, cur, id_sync, "COMMENCER")
        
#         _changer_statut(conn, cur, id_sync, "EN_COURS")
#         logger.info("Fenêtre de données : %s -> %s", fenetre_debut, fenetre_fin)
#         nb_lignes = synchroniser_tout(fenetre_debut, fenetre_fin) or 0        
#         update_synchronisation_resultat(
#             cur, id_sync, datetime.now(timezone.utc), nb_lignes, None
#         )
#         _changer_statut(conn, cur, id_sync, "TERMINER")
#         logger.info("Synchronisation terminée (%s lignes)", nb_lignes)
#         return True

#     except Exception as e:
#         logger.exception("Échec de la synchronisation automatique")
#         if conn is not None:
#             conn.rollback()
#             if id_sync is not None:
#                 try:
#                     update_synchronisation_resultat(
#                         cur, id_sync, datetime.now(timezone.utc), 0, str(e)
#                     )
#                     _changer_statut(conn, cur, id_sync, "ECHEC")
#                 except Exception:
#                     conn.rollback()
#                     logger.exception("Impossible d'enregistrer l'échec")
#         return False

#     finally:
#         if cur is not None:
#             cur.close()
#         if conn is not None:
#             close_connection(conn)
#         _verrou.release()

def executer_synchronisation():
    if not _verrou.acquire(blocking=False):
        logger.warning("Synchronisation déjà en cours, ce tour est ignoré")
        return False

    conn = None
    cur = None
    id_sync = None
    t_total = time.perf_counter()
    suivi = {"source": "google", "statut": "ECHEC", "erreur": None, "nb_lignes": 0}
    etapes = suivi.setdefault("etapes_s", {})

    try:
        conn = get_connection()
        cur = conn.cursor()
        source = "google"
        lancement = datetime.now(timezone.utc)

        with chrono("lecture_curseur", etapes):
            dernier = get_derniere_fenetre_fin_by_source(cur, source)

        if dernier is None:
            fenetre_debut = lancement - PREMIERE_SYNCHRO
            marge = None
        else:
            deja_fait_aujourdhui = (
                dernier.astimezone(TZ_LOCAL).date() == lancement.astimezone(TZ_LOCAL).date()
            )
            marge = MARGE_1h if deja_fait_aujourdhui else MARGE_72h
            fenetre_debut = dernier - marge
        fenetre_fin = lancement

        suivi.update({
            "lancement": lancement.isoformat(),
            "fenetre_debut": fenetre_debut.isoformat(),
            "fenetre_fin": fenetre_fin.isoformat(),
            "marge_heures": marge.total_seconds() / 3600 if marge else None,
            "fenetre_heures": round((fenetre_fin - fenetre_debut).total_seconds() / 3600, 2),
        })

        with chrono("insert_historique", etapes):
            id_sync = insert_synchronisation_historique(
                cur, source, lancement, fenetre_debut, fenetre_fin
            )
            _changer_statut(conn, cur, id_sync, "COMMENCER")
            _changer_statut(conn, cur, id_sync, "EN_COURS")
        suivi["id_sync"] = id_sync

        logger.info("Fenêtre de données : %s -> %s", fenetre_debut, fenetre_fin)

        with chrono("synchroniser_tout_total", etapes):
            nb_lignes = synchroniser_tout(fenetre_debut, fenetre_fin, suivi=suivi) or 0

        with chrono("update_resultat", etapes):
            update_synchronisation_resultat(
                cur, id_sync, datetime.now(timezone.utc), nb_lignes, None
            )
            _changer_statut(conn, cur, id_sync, "TERMINER")

        suivi.update({"statut": "TERMINER", "nb_lignes": nb_lignes})
        logger.info("Synchronisation terminée (%s lignes)", nb_lignes)
        return True

    except Exception as e:
        logger.exception("Échec de la synchronisation automatique")
        suivi["erreur"] = str(e)
        if conn is not None:
            conn.rollback()
            if id_sync is not None:
                try:
                    update_synchronisation_resultat(
                        cur, id_sync, datetime.now(timezone.utc), 0, str(e)
                    )
                    _changer_statut(conn, cur, id_sync, "ECHEC")
                except Exception:
                    conn.rollback()
                    logger.exception("Impossible d'enregistrer l'échec")
        return False

    finally:
        duree = time.perf_counter() - t_total
        suivi["duree_totale_s"] = round(duree, 3)
        if suivi["nb_lignes"] and duree > 0:
            suivi["lignes_par_seconde"] = round(suivi["nb_lignes"] / duree, 1)
        logger.info("Durées par étape : %s | total %.1fs", etapes, duree)
        # _sauver_suivi(suivi)

        if cur is not None:
            cur.close()
        if conn is not None:
            close_connection(conn)
        _verrou.release()

def auto_synchronisation(intervalle=INTERVALLE_SECONDES):
    """Boucle : synchronise, attend, recommence, jusqu'à l'arrêt."""
    while not _arret.is_set():
        executer_synchronisation()
        _arret.wait(intervalle)      


def demarrer_auto_synchronisation(intervalle=INTERVALLE_SECONDES):
    """À appeler une seule fois au démarrage de l'application."""
    global _thread
    if _thread is not None and _thread.is_alive():
        return _thread              
    _arret.clear()
    _thread = threading.Thread(
        target=auto_synchronisation,
        args=(intervalle,),
        daemon=True,
        name="auto-synchronisation",
    )
    _thread.start()
    return _thread


def arreter_auto_synchronisation(timeout=300):
    """Demande l'arrêt et attend la fin de la synchro en cours (5 min max)."""
    _arret.set()
    if _thread is not None:
        _thread.join(timeout=timeout)