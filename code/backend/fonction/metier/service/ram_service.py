from datetime import timedelta

from backend.fonction.conn.transaction import lecture
from backend.fonction.metier.repository.ram import (
    get_max_total_ram as get_max_total_ram_repository,
    get_latest_by_device as get_latest_by_device_repository,
    get_ram_device_date as get_ram_device_date_repository,
)
from backend.utils.format_valeur import usage_percent


def get_max_total_ram(id_device, datetime_from=None, datetime_to=None):
    with lecture() as cur:
        if cur is None:
            return None
        return get_max_total_ram_repository(cur, id_device, datetime_from, datetime_to)


def _serialize_latest_ram(row):
    if row is None:
        return None

    date_ram = row.get("date")
    ram_total = row.get("ram_total")
    ram_libre = row.get("ram_libre")
    ram_utiliser = row.get("ram_utiliser")
    if ram_utiliser is None and ram_total is not None and ram_libre is not None:
        ram_utiliser = max(ram_total - ram_libre, 0)

    return {
        "id": row.get("id"),
        "id_device": row.get("id_device"),
        "ram_total": ram_total,
        "ram_utiliser": ram_utiliser,
        "ram_libre": ram_libre,
        "utilisation_pct": usage_percent(ram_utiliser, ram_total),
        "date": str(date_ram) if date_ram else None,
    }


def get_latest_ram(id_device):
    with lecture() as cur:
        if cur is None:
            return None
        row = get_latest_by_device_repository(cur, id_device)
        return _serialize_latest_ram(row)


def get_ram_device_date(id_device, date_debut, date_fin):
    with lecture() as cur:
        if cur is None:
            return {"total": None, "same_day": True, "detail": []}
        mesures = get_ram_device_date_repository(cur, id_device, date_debut, date_fin)
        return _build_date_summary(mesures, date_debut, date_fin)


def _group_by_day(mesures, date_debut, date_fin):
    par_jour = {}
    for mesure in mesures:
        jour = mesure["date"].date()
        par_jour[jour] = par_jour.get(jour, 0) + mesure["valeur"]

    detail = []
    jour_courant = date_debut.date()
    jour_fin = date_fin.date()
    while jour_courant <= jour_fin:
        detail.append({"date": jour_courant.isoformat(), "valeur": par_jour.get(jour_courant)})
        jour_courant += timedelta(days=1)
    return detail


def _build_date_summary(mesures, date_debut, date_fin):
    if date_debut.date() == date_fin.date():
        detail = [
            {"datetime": mesure["date"].isoformat(), "valeur": mesure["valeur"]}
            for mesure in mesures
        ]
        return {"total": None, "same_day": True, "detail": detail}
    return {
        "total": sum(mesure["valeur"] for mesure in mesures),
        "same_day": False,
        "detail": _group_by_day(mesures, date_debut, date_fin),
    }


__all__ = [
    "get_max_total_ram",
    "get_latest_ram",
    "get_ram_device_date",
]
