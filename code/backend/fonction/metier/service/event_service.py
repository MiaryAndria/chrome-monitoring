import json
from datetime import datetime, timezone

from backend.fonction.conn.transaction import lecture, transaction
from backend.fonction.metier.repository.evenement import (
    get_liste_evenement_avec_details,
    get_liste_type_evenement,
    find_evenements_paginated,
    find_evenements_resolues_paginated,
    get_last_event_date,
    get_evenement_by_id,
    delete_evenements_statut,
    delete_evenement_device,
    get_evenement_detail_by_id,
    insert_evenement_statut,
    get_statut_evenement,
)

from backend.fonction.metier.repository.rapport import get_latest_battery_by_device
from backend.utils.pagination import build_page
from backend.core.cache import cache_get, cache_invalidate_prefix, cache_set
from backend.utils.datetime_tools import _to_utc, local_to_utc
from backend.utils.config_db import get_int_configuration
from backend.exceptions import ValidationError
from backend.fonction.metier.service.ia_evenement_service import stream_chat_with_ia
from backend.fonction.metier.repository.statut import ID_STATUT_RESOLUE, ID_STATUT_ACTIVE

def _get_statut_evenement(cur, id_evenement):
    row = get_statut_evenement(cur, id_evenement)
    if row is None:
        return None
    return row[2]

def _change_statut(id_evenement, id_statut):
    with transaction() as cur:
        if cur is None:
            return False
        if get_evenement_by_id(cur, id_evenement) is None:
            return False
        statut_evenement = _get_statut_evenement(cur, id_evenement)
        if statut_evenement == id_statut:
            raise ValidationError("Impossible de modifier le statut : transition refusée (statut déjà appliqué).")
        insert_evenement_statut(cur, id_evenement, id_statut)
    cache_invalidate_prefix("events:")
    cache_invalidate_prefix("events_resolues:")
    cache_invalidate_prefix("events_actives:")
    return True

def marquer_evenement_resolu(id_evenement):
    return _change_statut(id_evenement, ID_STATUT_RESOLUE)

def repasser_evenement_actif(id_evenement):
    return _change_statut(id_evenement, ID_STATUT_ACTIVE)    

def get_detail_evenement(id):
    with lecture() as cur:
        if cur is None:
            return None
        return get_evenement_detail_by_id(cur, id)


def get_event():
    with lecture() as cur:
        if cur is None:
            return []
        rows = get_liste_evenement_avec_details(cur)

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


def get_type_evenement():
    with lecture() as cur:
        if cur is None:
            return []
        rows = get_liste_type_evenement(cur)
        result = []
        for r in rows:
            result.append({
                "id":   r[0],
                "type": r[1]
            })
        return result


def _date_evenement_utc(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat()
    return str(value)


def _map_event_row(row):
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


def _fetch_page(fetch_fn, page, page_size, type_evenement, id_filiale, filiale,
                recherche, datetime_from, datetime_to, utilisateur_recent):
    with lecture() as cur:
        if cur is None:
            return build_page([], 0, page, page_size)
        rows, total = fetch_fn(
            cur,
            page=page,
            page_size=page_size,
            type_evenement=type_evenement,
            id_filiale=id_filiale,
            filiale=filiale,
            recherche=recherche,
            datetime_from=datetime_from,
            datetime_to=datetime_to,
            utilisateur_recent=utilisateur_recent,
        )
        return build_page([_map_event_row(row) for row in rows], total, page, page_size)


def _events_cache_key(prefix, page, page_size, type_evenement, id_filiale, filiale,
                      recherche, datetime_from, datetime_to, utilisateur_recent):
    return (
        f"{prefix}:{page}:{page_size}:{type_evenement}:{id_filiale}:{filiale}:"
        f"{recherche}:{datetime_from}:{datetime_to}:{utilisateur_recent}"
    )


def _get_page_cached(prefix, fetch_fn, page, page_size, type_evenement, id_filiale,
                     filiale, recherche, datetime_from, datetime_to, utilisateur_recent):
    offset = get_int_configuration("TZ_OFFSET", 3)
    datetime_from = local_to_utc(datetime_from, offset)
    datetime_to = local_to_utc(datetime_to, offset)

    cle = _events_cache_key(
        prefix, page, page_size, type_evenement, id_filiale, filiale,
        recherche, datetime_from, datetime_to, utilisateur_recent
    )
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    resultat = _fetch_page(
        fetch_fn, page, page_size, type_evenement, id_filiale, filiale,
        recherche, datetime_from, datetime_to, utilisateur_recent
    )
    return cache_set(cle, resultat)


def get_events_page(page=1, page_size=10, type_evenement=None, id_filiale=None,
                    filiale=None, recherche=None, datetime_from=None,
                    datetime_to=None, utilisateur_recent=None):
    return _get_page_cached(
        "events", find_evenements_paginated, page, page_size, type_evenement, id_filiale,
        filiale, recherche, datetime_from, datetime_to, utilisateur_recent,
    )


def get_evenements_resolues_page(page=1, page_size=10, type_evenement=None, id_filiale=None,
                                 filiale=None, recherche=None, datetime_from=None,
                                 datetime_to=None, utilisateur_recent=None):
    return _get_page_cached(
        "events_resolues", find_evenements_resolues_paginated, page, page_size, type_evenement,
        id_filiale, filiale, recherche, datetime_from, datetime_to, utilisateur_recent,
    )


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
    with lecture() as cur:
        if cur is None:
            return None
        evenement = get_evenement_by_id(cur, event_id)
        if evenement is None:
            return None

        id_device = evenement[1]
        return _build_duree_vie(cur, id_device)


def delete_evenement(date_limite):
    with transaction() as cur:
        if cur is None:
            return 0
        delete_evenements_statut(cur, date_limite)
        delete_evenement_device(cur,date_limite)
    cache_invalidate_prefix("events:")
    cache_invalidate_prefix("events_resolues:")


def get_evenement_ia_context(event_id):
    with lecture() as cur:
        if cur is None:
            return None
        return get_evenement_detail_by_id(cur, event_id)


def ia_chat_stream(event_id, messages):
    evenement = get_evenement_ia_context(event_id)
    if evenement is None:
        return None
    return stream_chat_with_ia(evenement, messages)


__all__ = [
    "get_events_page",
    "get_evenements_resolues_page",
    "get_duree_vie_evenement",
    "compute_battery_remaining",
    "get_evenement_ia_context",
    "ia_chat_stream",
    "marquer_evenement_resolu",
    "repasser_evenement_actif",
]
