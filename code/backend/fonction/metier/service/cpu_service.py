from datetime import timedelta

from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.cpu import (
    get_latest_by_device as get_latest_by_device_repository,
    get_cpu_device_date as get_cpu_device_date_repository,
)


def _serialize_latest_cpu(row):
    if row is None:
        return None

    date_cpu = row.get("date")
    utilisation = row.get("cpu_utiliser")

    return {
        "id": row.get("id"),
        "id_device": row.get("id_device"),
        "cpu_model": row.get("cpu_model"),
        "freq_max_proc": row.get("freq_max_proc"),
        "cpu_architecture": row.get("cpu_architecture"),
        "cpu_utiliser": float(utilisation) if utilisation is not None else None,
        "cpu_libre": row.get("cpu_libre"),
        "cpu_total": row.get("cpu_total"),
        "date": str(date_cpu) if date_cpu else None,
    }


def get_latest_cpu(id_device):
    connexion = get_connection()
    if connexion is None:
        return None
    try:
        cur = connexion.cursor()
        row = get_latest_by_device_repository(cur, id_device)
        cur.close()
        return _serialize_latest_cpu(row)
    finally:
        close_connection(connexion)


def get_cpu_device_date(id_device, date_debut, date_fin):
    connexion = get_connection()
    if connexion is None:
        return {"total": None, "same_day": True, "detail": []}
    try:
        cur = connexion.cursor()
        mesures = get_cpu_device_date_repository(cur, id_device, date_debut, date_fin)
        cur.close()
        return _build_date_summary(mesures, date_debut, date_fin)
    finally:
        close_connection(connexion)


def _group_by_day(mesures, date_debut, date_fin):
    par_jour = {}
    for mesure in mesures:
        jour = mesure["date"].date()
        par_jour[jour] = par_jour.get(jour, 0.0) + mesure["valeur"]

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


__all__ = ["get_latest_cpu", "get_cpu_device_date"]
