import logging

from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.alerte import (
    get_alerte_by_type,
    insert_alerte,
    insert_alerte_statut,
    get_temperature_max_device,
    get_liste_device_alerte_by_date,
    get_device_alerte_active_by_device_and_alerte,
    get_nombre_alerte_active,
    insert_device_alerte,
    insert_device_alerte_statut,
    get_dernieres_alertes,
    find_device_alertes_paginated,
    find_device_alertes_resolues_paginated,
    _compter_alertes,
    get_liste_device_alerte_by_date_resolue,
    get_nombre_alerte_resolue,
    get_type_alerte,
)
from backend.fonction.metier.repository.cpu import get_latest_by_device as get_latest_cpu
from backend.fonction.metier.repository.ram import get_latest_by_device as get_latest_ram
from backend.fonction.metier.repository.disk import get_latest_by_device as get_latest_disk
from backend.fonction.metier.repository.rapport import get_latest_battery_by_device
from backend.fonction.metier.repository.evenement import count_evenements_device_period
from backend.fonction.metier.repository.seuil import get_liste_seuil, get_regles_seuil
from backend.fonction.metier.repository.devices import (
    get_liste_device,
    get_utilisateur_recent_by_device,
)
from backend.fonction.metier.repository.statut import get_statut_by_name
from backend.utils.config_db import get_int_configuration
from backend.utils.format_valeur import usage_percent
from backend.utils.pagination import build_page
from backend.core.cache import cache_get, cache_set, cache_invalidate_prefix
from backend.utils.builder import _serialize_alerte_resume

# Noms de statuts (t_statut.nom) : les ids sont resolus en base, jamais codes en dur
NOM_STATUT_ACTIVE = "ACTIVE"
NOM_STATUT_RESOLUE = "RESOLUE"
NOM_STATUT_CREER = "CREER"

# Cle de configuration : fenetre (jours) du seuil d'evenements.
CLE_FENETRE_EVENEMENTS = "ALERTE_EVENEMENTS_FENETRE_JOURS"
FENETRE_EVENEMENTS_DEFAUT = 7

logger = logging.getLogger(__name__)


def _id_statut(cur, nom):
    row = get_statut_by_name(cur, nom)
    return row[0] if row else None


def _get_or_create_alerte(cur, type_):
    existante = get_alerte_by_type(cur, type_)
    if existante is not None:
        return existante[0]
    id_alerte = insert_alerte(cur, type_)
    if id_alerte is not None:
        insert_alerte_statut(cur, id_alerte, _id_statut(cur, NOM_STATUT_CREER))
    return id_alerte

def getNombreAlerte():
    connexion = get_connection()
    if connexion is None:
        return 0
    try:
        cur = connexion.cursor()
        return get_nombre_alerte_active(cur)
    finally:
        close_connection(connexion)

def getNombreAlerteResolue():
    connexion = get_connection()
    if connexion is None :
        return 0
    try:
        cur = connexion.cursor()
        return get_nombre_alerte_resolue(cur)
    finally:
        close_connection(connexion)
        
def getTypeAlerte():
    connexion = get_connection()
    if connexion is None :
        return []
    try:
        result = []
        cur=connexion.cursor()
        t = get_type_alerte(cur)
        for type in t:
            result.append({
                "id":type[0],
                "type":type[1],
            })
        return result 
    finally:
        close_connection(connexion)

def getDernieresAlertes(limit):
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_dernieres_alertes(cur, limit)
        return [_serialize_alerte_resume(r) for r in rows]
    finally:
        close_connection(connexion)


def getListeDeviceAlerteDate(date_debut=None, date_fin=None):
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_liste_device_alerte_by_date(cur, date_debut, date_fin)
        return [_serialize_alerte_resume(r) for r in rows]
    finally:
        close_connection(connexion)

def getListeDeviceAlerteDateResolue(date_debut=None, date_fin=None):
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_liste_device_alerte_by_date_resolue(cur, date_debut, date_fin)
        return [_serialize_alerte_resume(r) for r in rows]
    finally:
        close_connection(connexion)
        
def _fetch_device_alertes_page(page, page_size, date_debut, date_fin,type,search):
    connexion = get_connection()
    if connexion is None:
        return build_page([], 0, page, page_size)
    try:
        cur = connexion.cursor()
        rows = find_device_alertes_paginated(cur, page, page_size, date_debut, date_fin,type,search)
        total = rows[0][7] if rows else 0
        items = [_serialize_alerte_resume(r) for r in rows]
        return build_page(items, total, page, page_size)
    finally:
        close_connection(connexion)

def getDeviceAlertesPage(page=1, page_size=10, date_debut=None, date_fin=None,type=None,search=None):
    cle = f"alertes:device:{page}:{page_size}:{date_debut}:{date_fin}:{type}:{search}"
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur
    return cache_set(cle, _fetch_device_alertes_page(page, page_size, date_debut, date_fin,type,search))


def _fetch_device_alertes_resolues_page(page, page_size, date_debut, date_fin,type,search):
    connexion = get_connection()
    if connexion is None:
        return build_page([], 0, page, page_size)
    try:
        cur = connexion.cursor()
        rows = find_device_alertes_resolues_paginated(cur, page, page_size, date_debut, date_fin,type,search)
        total = rows[0][7] if rows else 0
        items = [_serialize_alerte_resume(r) for r in rows]
        return build_page(items, total, page, page_size)
    finally:
        close_connection(connexion)


def getDeviceAlertesResoluesPage(page=1, page_size=10, date_debut=None, date_fin=None,type=None,search=None):
    cle = f"alertes:device:resolues:{page}:{page_size}:{date_debut}:{date_fin}:{type}:{search}"
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur
    return cache_set(cle, _fetch_device_alertes_resolues_page(page, page_size, date_debut, date_fin,type,search))


def _seuils_actifs(cur):
    # get_liste_seuil renvoie (id, id_type_seuil, type, categorie, valeur, date, sens)
    seuils = {}
    for ligne in get_liste_seuil(cur):
        type_seuil = ligne[2]
        valeur = ligne[4]
        seuils[type_seuil] = valeur
    return seuils


def _metrique_cpu(cur, id_device):
    cpu = get_latest_cpu(cur, id_device)
    return float(cpu["cpu_utiliser"]) if cpu and cpu.get("cpu_utiliser") is not None else None


def _metrique_ram(cur, id_device):
    ram = get_latest_ram(cur, id_device)
    return usage_percent(ram.get("ram_utiliser"), ram.get("ram_total")) if ram else None


def _metrique_temperature(cur, id_device):
    return get_temperature_max_device(cur, id_device)


def _metrique_stockage(cur, id_device):
    disk = get_latest_disk(cur, id_device)
    return usage_percent(disk.get("total_utiliser"), disk.get("total_reel")) if disk else None


def _metrique_sante_batterie(cur, id_device):
    batterie = get_latest_battery_by_device(cur, id_device)
    donnees = (batterie or {}).get("donnees") or {}
    return usage_percent(donnees.get("fullChargeCapacity"), donnees.get("designCapacity"))


def _metrique_batterie(cur, id_device):
    batterie = get_latest_battery_by_device(cur, id_device)
    donnees = (batterie or {}).get("donnees") or {}
    echantillons = donnees.get("sample") or []
    premier = echantillons[0] if echantillons and isinstance(echantillons[0], dict) else None
    if premier is None:
        return None
    return usage_percent(premier.get("remainingCapacity"), donnees.get("fullChargeCapacity"))


def _metrique_tache_print(cur, id_device):
    # Aucune donnee de tache d'impression persistee -> inactif pour l'instant.
    return None


def _metrique_evenements(cur, id_device, jours_evenements):
    return count_evenements_device_period(cur, id_device, jours_evenements)


def _metriques_device(cur, id_device, jours_evenements):
    return {
        "cpu": _metrique_cpu(cur, id_device),
        "ram": _metrique_ram(cur, id_device),
        "temperature": _metrique_temperature(cur, id_device),
        "stockage": _metrique_stockage(cur, id_device),
        "sante_batterie": _metrique_sante_batterie(cur, id_device),
        "batterie": _metrique_batterie(cur, id_device),
        "tache_print": _metrique_tache_print(cur, id_device),
        "evenements": _metrique_evenements(cur, id_device, jours_evenements),
    }


def _appliquer_etat(cur, id_device, id_alerte, message, depasse,
                    id_statut_active, id_statut_resolue):
    active = get_device_alerte_active_by_device_and_alerte(cur, id_device, id_alerte)
    if depasse and active is None:
        id_device_alerte = insert_device_alerte(cur, id_device, id_alerte, message)
        insert_device_alerte_statut(cur, id_device_alerte, id_statut_active)
    elif (not depasse) and active is not None:
        insert_device_alerte_statut(cur, active[0], id_statut_resolue)

def _executer_moteur(cur):
    id_statut_active = _id_statut(cur, NOM_STATUT_ACTIVE)
    id_statut_resolue = _id_statut(cur, NOM_STATUT_RESOLUE)

    try:
        regles = get_regles_seuil(cur)
    except Exception:
        logger.exception(
            "Lecture des regles d'alerte impossible "
            "(colonnes sens/type_alerte/metrique/message absentes de t_type_seuil ?)"
        )
        return

    seuils = _seuils_actifs(cur)
    jours_evenements = get_int_configuration(CLE_FENETRE_EVENEMENTS, FENETRE_EVENEMENTS_DEFAUT)

    # Regles actives : on ne cree PAS encore le type d'alerte ici.
    # Il sera cree au premier device qui a reellement une valeur (evite les
    # types "fantomes" comme ALERTE_TACHE_PRINT qui renvoie toujours None).
    regles_actives = []
    for cle_seuil, type_alerte, metrique, sens, message in regles:
        valeur_seuil = seuils.get(cle_seuil)
        if valeur_seuil is None:
            continue
        regle = {
            "type_alerte": type_alerte,
            "metrique": metrique,
            "sens": sens,
            "valeur_seuil": valeur_seuil,
            "message": message,
            "id_alerte": None,
        }
        regles_actives.append(regle)

    for device in get_liste_device(cur):
        id_device = device[0]
        metriques = _metriques_device(cur, id_device, jours_evenements)
        for regle in regles_actives:
            valeur = metriques.get(regle["metrique"])
            if valeur is None:
                continue
            if regle["id_alerte"] is None:
                regle["id_alerte"] = _get_or_create_alerte(cur, regle["type_alerte"])
            if regle["sens"] == "<":
                depasse = valeur < regle["valeur_seuil"]
            else:
                depasse = valeur > regle["valeur_seuil"]
            _appliquer_etat(
                cur, id_device, regle["id_alerte"], regle["message"], depasse,
                id_statut_active, id_statut_resolue,
            )

def insertAlerte(cur):
    _executer_moteur(cur)
    cache_invalidate_prefix("alertes:")


def getNombreAlerteParType(type_alerte, statut="active", date_debut=None, date_fin=None):
    # Meme reference de statut que les listes (device_alerte.py) : 1 = active, 15 = resolue.
    id_statut = 15 if statut == "resolue" else 1
    connexion = get_connection()
    if connexion is None:
        return 0
    try:
        cur = connexion.cursor()
        return _compter_alertes(cur, type_alerte, id_statut, date_debut, date_fin)
    finally:
        close_connection(connexion)
