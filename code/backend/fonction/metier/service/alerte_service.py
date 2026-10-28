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
from backend.fonction.metier.repository.seuil import get_liste_seuil
from backend.fonction.metier.repository.devices import (
    get_liste_device,
    get_utilisateur_recent_by_device,
)
from backend.fonction.metier.repository.statut import get_statut_by_name
from backend.utils.format_valeur import usage_percent
from backend.utils.pagination import build_page
from backend.core.cache import cache_get, cache_set, cache_invalidate_prefix
from backend.utils.builder import _serialize_alerte_resume

# Clés de seuils (t_seuil.cle) : lien métrique -> seuil.
# Le NOM de la clé est la référence ; la VALEUR est lue en base (repository seuil).
SEUIL_CPU = "seuil_utilisation_cpu"
SEUIL_RAM = "seuil_utilisation_ram"
SEUIL_TEMPERATURE = "seuil_capteur_cpu"

# Types d'alerte (t_alerte.type)
TYPE_ALERTE_CPU = "ALERTE_CPU"
TYPE_ALERTE_RAM = "ALERTE_RAM"
TYPE_ALERTE_TEMPERATURE = "ALERTE_TEMPERATURE"

# Noms de statuts (t_statut.nom) : les ids sont résolus en base, jamais codés en dur
NOM_STATUT_ACTIVE = "ACTIVE"
NOM_STATUT_RESOLUE = "RESOLUE"
NOM_STATUT_CREER = "CREER"


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
    return {r[1]: r[2] for r in get_liste_seuil(cur)}


def _metriques_device(cur, id_device):
    cpu = get_latest_cpu(cur, id_device)
    ram = get_latest_ram(cur, id_device)
    cpu_pct = float(cpu["cpu_utiliser"]) if cpu and cpu.get("cpu_utiliser") is not None else None
    ram_pct = usage_percent(ram.get("ram_utiliser"), ram.get("ram_total")) if ram else None
    return {
        "cpu": cpu_pct,
        "ram": ram_pct,
        "temperature": get_temperature_max_device(cur, id_device),
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

    seuils = _seuils_actifs(cur)
    valeur_cpu = seuils.get(SEUIL_CPU)
    valeur_ram = seuils.get(SEUIL_RAM)
    valeur_temperature = seuils.get(SEUIL_TEMPERATURE)

    id_alerte_cpu = _get_or_create_alerte(cur, TYPE_ALERTE_CPU) if valeur_cpu is not None else None
    id_alerte_ram = _get_or_create_alerte(cur, TYPE_ALERTE_RAM) if valeur_ram is not None else None
    id_alerte_temperature = (
        _get_or_create_alerte(cur, TYPE_ALERTE_TEMPERATURE) if valeur_temperature is not None else None
    )

    for device in get_liste_device(cur):
        id_device = device[0]
        metriques = _metriques_device(cur, id_device)

        if id_alerte_cpu is not None and metriques["cpu"] is not None:
            _appliquer_etat(
                cur, id_device, id_alerte_cpu,
                "Utilisation CPU supérieure au seuil",
                metriques["cpu"] > valeur_cpu,
                id_statut_active, id_statut_resolue,
            )

        if id_alerte_ram is not None and metriques["ram"] is not None:
            _appliquer_etat(
                cur, id_device, id_alerte_ram,
                "Utilisation RAM supérieure au seuil",
                metriques["ram"] > valeur_ram,
                id_statut_active, id_statut_resolue,
            )

        if id_alerte_temperature is not None and metriques["temperature"] is not None:
            _appliquer_etat(
                cur, id_device, id_alerte_temperature,
                "Température capteur CPU supérieure au seuil",
                metriques["temperature"] > valeur_temperature,
                id_statut_active, id_statut_resolue,
            )

def insertAlerte(cur):
    _executer_moteur(cur)
    cache_invalidate_prefix("alertes:")
    
def getStatsAlerteCpuActive(date_debut=None, date_fin=None):
    connexion = get_connection()
    if connexion is None:
        return 0
    try:
        cur = connexion.cursor()
        return _compter_alertes(cur, "ALERTE_CPU", 1, date_debut, date_fin)
    finally:
        close_connection(connexion)


def getStatsAlerteRamActive(date_debut=None, date_fin=None):
    connexion = get_connection()
    if connexion is None:
        return 0
    try:
        cur = connexion.cursor()
        return _compter_alertes(cur, "ALERTE_RAM", 1, date_debut, date_fin)
    finally:
        close_connection(connexion)


def getStatsAlerteTemperatureActive(date_debut=None, date_fin=None):
    connexion = get_connection()
    if connexion is None:
        return 0
    try:
        cur = connexion.cursor()
        return _compter_alertes(cur, "ALERTE_TEMPERATURE", 1, date_debut, date_fin)
    finally:
        close_connection(connexion)


def getStatsAlerteCpuResolue(date_debut=None, date_fin=None):
    connexion = get_connection()
    if connexion is None:
        return 0
    try:
        cur = connexion.cursor()
        return _compter_alertes(cur, "ALERTE_CPU", 15, date_debut, date_fin)
    finally:
        close_connection(connexion)


def getStatsAlerteRamResolue(date_debut=None, date_fin=None):
    connexion = get_connection()
    if connexion is None:
        return 0
    try:
        cur = connexion.cursor()
        return _compter_alertes(cur, "ALERTE_RAM", 15, date_debut, date_fin)
    finally:
        close_connection(connexion)


def getStatsAlerteTemperatureResolue(date_debut=None, date_fin=None):
    connexion = get_connection()
    if connexion is None:
        return 0
    try:
        cur = connexion.cursor()
        return _compter_alertes(cur, "ALERTE_TEMPERATURE", 15, date_debut, date_fin)
    finally:
        close_connection(connexion)

