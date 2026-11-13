from backend.fonction.conn.transaction import lecture
from backend.fonction.metier.repository.disk import (
    get_latest_by_device as get_latest_by_device_repository,
)


def _serialize_latest_disk(row):
    if row is None:
        return None

    date_disk = row.get("date")

    return {
        "id": row.get("id"),
        "id_device": row.get("id_device"),
        "id_disk": row.get("id_disk"),
        "disk_model": row.get("disk_model"),
        "disk_type": row.get("disk_type"),
        "disponible": row.get("disponible"),
        "total_reel": row.get("total_reel"),
        "total_utiliser": row.get("total_utiliser"),
        "disponible_formater": row.get("disponible_formater"),
        "total_formater": row.get("total_formater"),
        "total_utiliser_formater": row.get("total_utiliser_formater"),
        "date": str(date_disk) if date_disk else None,
    }


def get_latest_disk(id_device):
    with lecture() as cur:
        if cur is None:
            return None
        row = get_latest_by_device_repository(cur, id_device)
        return _serialize_latest_disk(row)


__all__ = ["get_latest_disk"]
