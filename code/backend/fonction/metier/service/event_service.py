import json
from datetime import datetime, timezone

from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.evenement import (
    get_liste_evenement_avec_details,
    get_liste_type_evenement,
    find_evenements_paginated,
    get_last_event_date,
    get_evenement_by_id,
)
from backend.fonction.metier.repository.rapport import get_latest_battery_by_device
from backend.utils.pagination import build_page
from backend.core.cache import cache_get, cache_set

def get_event():
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_liste_evenement_avec_details(cur)
        cur.close()

        result = []
        for r in rows:
            details_raw = r[2]
            details = {}
            if details_raw:
                try:
                    details = json.loads(details_raw) if isinstance(details_raw, str) else details_raw
                except Exception:
                    details = {}

            result.append({
                "id":             r[0],
                "date_evenement": str(r[1]) if r[1] else None,
                "type_evenement": r[3],
                "device_id":      r[4],
                "serial_number":  r[5],
                "modele":         r[6],
                "filiale":        r[7],
                "cause_class":    details.get("cause_class"),
                "cause_hint":     details.get("cause_hint"),
                "last_user":      details.get("last_user"),
                "incident_key":   details.get("incident_key"),
                "crash_seq":      details.get("crash_seq"),
                "raw_events":     details.get("raw_events"),
                "minutes_since_boot": details.get("minutes_since_boot"),
            })
        return result
    finally:
        close_connection(connexion)
        
def get_type_evenement():
    connexion = None
    try:
        connexion = get_connection()
        cur = connexion.cursor()
        rows = get_liste_type_evenement(cur)
        cur.close()
        result = []
        for r in rows:
            result.append({
                "id":   r[0],   
                "type": r[1]   
            })
        return result           
    finally:
        if connexion:          
            close_connection(connexion)


def _date_evenement_utc(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat()
    return str(value)


def _serialize_evenement_row(row):
    details = row.get("details") or {}
    if isinstance(details, str):
        try:
            details = json.loads(details)
        except Exception:
            details = {}

    date_evenement = row.get("date_evenement")

    return {
        "id": row.get("id"),
        "date_evenement": _date_evenement_utc(date_evenement),
        "type_evenement": row.get("type_evenement"),
        "device_id": row.get("device_id"),
        "serial_number": row.get("serial_number"),
        "modele": row.get("modele"),
        "filiale": row.get("filiale"),
        "cause_class": details.get("cause_class"),
        "cause_hint": details.get("cause_hint"),
        "last_user": details.get("last_user"),
        "incident_key": details.get("incident_key"),
        "crash_seq": details.get("crash_seq"),
        "raw_events": details.get("raw_events"),
        "minutes_since_boot": details.get("minutes_since_boot"),
    }


def _fetch_events_page(page=1, page_size=10, type_evenement=None, id_filiale=None,
                       filiale=None, recherche=None, datetime_from=None,
                       datetime_to=None):
    connexion = get_connection()
    if connexion is None:
        return build_page([], 0, page, page_size)
    try:
        cur = connexion.cursor()
        rows = find_evenements_paginated(
            cur, page, page_size, type_evenement, id_filiale, filiale,
            recherche, datetime_from, datetime_to
        )
        total = rows[0]["total"] if rows else 0
        items = [_serialize_evenement_row(row) for row in rows]
        cur.close()
        return build_page(items, total, page, page_size)
    finally:
        close_connection(connexion)


def _events_cache_key(page, page_size, type_evenement, id_filiale, filiale,
                      recherche, datetime_from, datetime_to):
    return (
        f"events:{page}:{page_size}:{type_evenement}:{id_filiale}:{filiale}:"
        f"{recherche}:{datetime_from}:{datetime_to}"
    )


def get_events_page(page=1, page_size=10, type_evenement=None, id_filiale=None,
                    filiale=None, recherche=None, datetime_from=None,
                    datetime_to=None):
    cle = _events_cache_key(
        page, page_size, type_evenement, id_filiale, filiale,
        recherche, datetime_from, datetime_to
    )
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    resultat = _fetch_events_page(
        page, page_size, type_evenement, id_filiale, filiale,
        recherche, datetime_from, datetime_to
    )
    return cache_set(cle, resultat)


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _find_discharging_sample(samples):
    for sample in samples or []:
        if not isinstance(sample, dict):
            continue
        if (sample.get("status") or "").lower() != "discharging":
            continue

        courant = _to_float(sample.get("current"))
        capacite = _to_float(sample.get("remainingCapacity"))
        if courant is None or capacite is None or courant <= 0:
            continue

        return {
            "minutes_restantes": round(capacite / courant * 60, 1),
            "charge_rate": _to_float(sample.get("chargeRate")),
            "report_time": sample.get("reportTime"),
        }

    return None


def compute_battery_remaining(donnees):
    if not isinstance(donnees, dict):
        return None

    echantillons = donnees.get("sample") or []
    premier = echantillons[0] if echantillons and isinstance(echantillons[0], dict) else {}
    charge_rate = _to_float(premier.get("chargeRate"))
    estimation = _find_discharging_sample(echantillons)

    return {
        "etat": premier.get("status") or "Inconnu",
        "charge_rate": int(charge_rate) if charge_rate is not None else None,
        "battery_health": donnees.get("batteryHealth"),
        "cycle_count": donnees.get("cycleCount"),
        "minutes_restantes": estimation["minutes_restantes"] if estimation else None,
        "estimation_batterie": estimation,
        "report_time": donnees.get("reportTime"),
    }


def _to_utc(value):
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _build_duree_vie(cur, id_device):
    batterie = get_latest_battery_by_device(cur, id_device)
    dernier_evenement = get_last_event_date(cur, id_device)

    dernier_evenement_utc = _to_utc(dernier_evenement)
    secondes = None
    if dernier_evenement_utc is not None:
        ecart = datetime.now(timezone.utc) - dernier_evenement_utc
        secondes = max(int(ecart.total_seconds()), 0)

    donnees_batterie = batterie.get("donnees") if batterie else None
    details_batterie = compute_battery_remaining(donnees_batterie)

    minutes = details_batterie["minutes_restantes"] if details_batterie else None

    return {
        "duree_vie": minutes,
        "unite": "minutes",
        "details": {
            "batterie": details_batterie,
            "dernier_evenement": (
                dernier_evenement_utc.isoformat() if dernier_evenement_utc else None
            ),
            "secondes_depuis_dernier_evenement": secondes,
        },
    }


def get_duree_vie_evenement(event_id):
    connexion = get_connection()
    if connexion is None:
        return None
    try:
        cur = connexion.cursor()
        evenement = get_evenement_by_id(cur, event_id)
        if evenement is None:
            return None

        id_device = evenement[1]
        resultat = _build_duree_vie(cur, id_device)
        cur.close()
        return resultat
    finally:
        close_connection(connexion)


__all__ = [
    "get_events_page",
    "get_duree_vie_evenement",
    "compute_battery_remaining",
]
        