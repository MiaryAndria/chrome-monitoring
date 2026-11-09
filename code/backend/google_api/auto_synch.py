import logging
import threading
from datetime import datetime, timedelta, timezone
import time
# from backend.utils.save_to_json import save_to_json
from backend.utils.chrono import chrono
from backend.utils.config_db import get_configuration, get_int_configuration

from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.statut.constants import (
    ID_STATUT_COMMENCER,
    ID_STATUT_EN_COURS,
    ID_STATUT_TERMINER,
    ID_STATUT_ECHEC,
)
from backend.fonction.metier.service.import_service import synchroniser_tout
from backend.fonction.metier.repository.synchronisation import (
    get_derniere_fenetre_fin_by_source,
    insert_synchronisation_historique,
    insert_synchronisation_statut,
    update_synchronisation_resultat,
)
from backend.fonction.metier.service.event_service import delete_evenement
from backend.fonction.metier.service.alerte_service import delete_alerte



logger = logging.getLogger(__name__)

# Valeurs par defaut (utilisees si la cle n'existe pas / n'est pas lisible)
INTERVALLE_DEFAUT = 2 * 60
MARGE_JOUR_DEFAUT = 1
MARGE_HISTORIQUE_DEFAUT = 72
PREMIERE_FENETRE_JOURS_DEFAUT = 90
TZ_OFFSET_DEFAUT = 3
SOURCE_DEFAUT = "google"
CONFIG_SUPPRESSION_JOURS_DEFAUT = 30  

_verrou = threading.Lock()           # empêche deux synchros en même temps
_arret = threading.Event()           # pour arrêter proprement la boucle
_thread = None


def _tz_local():
    return timezone(timedelta(hours=get_int_configuration("TZ_OFFSET", TZ_OFFSET_DEFAUT)))


def _changer_statut(conn, cur, id_sync, id_statut):
    insert_synchronisation_statut(cur, id_statut, id_sync, datetime.now(timezone.utc))
    conn.commit()

def get_config_date_suppression():
    jours = get_int_configuration("CONFIGURATION_SUPPRESSION", CONFIG_SUPPRESSION_JOURS_DEFAUT)
    return timedelta(days=jours)


def executer_synchronisation():
    if not _verrou.acquire(blocking=False):
        logger.warning("Synchronisation déjà en cours, ce tour est ignoré")
        return False

    conn = None
    cur = None
    id_sync = None
    t_total = time.perf_counter()

    source = get_configuration("SYNC_SOURCE", SOURCE_DEFAUT)
    tz_local = _tz_local()
    premiere = timedelta(days=get_int_configuration("SYNC_PREMIERE_FENETRE_JOURS", PREMIERE_FENETRE_JOURS_DEFAUT))
    marge_historique = timedelta(hours=get_int_configuration("SYNC_MARGE_HEURES_HISTORIQUE", MARGE_HISTORIQUE_DEFAUT))
    marge_jour = timedelta(hours=get_int_configuration("SYNC_MARGE_HEURES_JOUR", MARGE_JOUR_DEFAUT))

    suivi = {"source": source, "statut": "ECHEC", "erreur": None, "nb_lignes": 0}
    etapes = suivi.setdefault("etapes_s", {})

    try:
        conn = get_connection()
        cur = conn.cursor()
        lancement = datetime.now(timezone.utc)

        with chrono("lecture_curseur", etapes):
            dernier = get_derniere_fenetre_fin_by_source(cur, source)

        if dernier is None:
            fenetre_debut = lancement - premiere
            marge = None
        else:
            deja_fait_aujourdhui = (
                dernier.astimezone(tz_local).date() == lancement.astimezone(tz_local).date()
            )
            marge = marge_jour if deja_fait_aujourdhui else marge_historique
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
            _changer_statut(conn, cur, id_sync, ID_STATUT_COMMENCER)
            _changer_statut(conn, cur, id_sync, ID_STATUT_EN_COURS)
        suivi["id_sync"] = id_sync

        logger.info("Fenêtre de données : %s -> %s", fenetre_debut, fenetre_fin)

        with chrono("synchroniser_tout_total", etapes):
            nb_lignes = synchroniser_tout(fenetre_debut, fenetre_fin, suivi=suivi) or 0

        with chrono("update_resultat", etapes):
            update_synchronisation_resultat(
                cur, id_sync, datetime.now(timezone.utc), nb_lignes, None
            )
            _changer_statut(conn, cur, id_sync, ID_STATUT_TERMINER)

        suivi.update({"statut": "TERMINER", "nb_lignes": nb_lignes})
        logger.info("Synchronisation terminée (%s lignes)", nb_lignes)
        
        try:
            date_limite = datetime.now(timezone.utc) - get_config_date_suppression()
            delete_evenement(date_limite)
            delete_alerte(date_limite)
        except Exception:
            logger.exception("Purge des données anciennes échouée")

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
                    _changer_statut(conn, cur, id_sync, ID_STATUT_ECHEC)
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


def auto_synchronisation(intervalle=None):
    while not _arret.is_set():
        executer_synchronisation()
        attente = intervalle
        if attente is None:
            attente = get_int_configuration("SYNC_INTERVALLE_SECONDES", INTERVALLE_DEFAUT)
        _arret.wait(attente)


def demarrer_auto_synchronisation(intervalle=None):
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
