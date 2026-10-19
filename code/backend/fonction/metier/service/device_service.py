from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.devices import (
    get_device_by_id,
    get_device_by_device_id,
    get_liste_device,
    recherche_multicritere,
    find_devices_paginated,
)
from backend.utils.builder import _build_device_response
from backend.utils.format_valeur import format_bytes, format_frequency
from backend.utils.pagination import build_page
from backend.core.cache import cache_get, cache_set

def getListeDevice():
    connexion = get_connection()
    if connexion is None:
        print("Connexion BDD impossible")
        return []
    cur = connexion.cursor()
    try:
        devices = get_liste_device(cur)
        return [payload for d in devices if (payload := _build_device_response(cur, d)) is not None]
    finally:
        close_connection(connexion)

def getDeviceDetail(id):
    connexion = get_connection()
    if connexion is None:
        print("Connexion BDD IMPOSSIBLE")
        return None
    try:
        cur = connexion.cursor()
        d = get_device_by_id(cur, id)
        return _build_device_response(cur, d)
    finally:
        close_connection(connexion)


def getDeviceFiltered(recherche):
    connexion = get_connection()
    if connexion is None:
        print("Connexion BDD IMPOSSIBLE")
        return []
    try:
        cur = connexion.cursor()
        devices = recherche_multicritere(cur, recherche)
        if not devices:
            return []

        result = []
        for d in devices:
            payload = _build_device_response(cur, get_device_by_id(cur, d[0]))
            if payload:
                result.append(payload)
        return result
    finally:
        close_connection(connexion)


def _serialize_device_row(row):
    ram_total = row.get("ram_total")
    disk_total = row.get("disk_total")
    disk_free = row.get("disk_free")
    disk_used = row.get("disk_used")

    if disk_free is None and disk_total is not None and disk_used is not None:
        disk_free = max(disk_total - disk_used, 0)
    if disk_used is None and disk_total is not None and disk_free is not None:
        disk_used = max(disk_total - disk_free, 0)

    date_creation = row.get("date")

    return {
        "id": row.get("id"),
        "id_device": row.get("device_id"),
        "serial_number": row.get("serial_number"),
        "modele": row.get("modele"),
        "id_type_appareil": row.get("id_type_appareil"),
        "type_appareil": row.get("type_appareil"),
        "chromeos_version": row.get("chromeos_version"),
        "chrome_version": row.get("chrome_version"),
        "mac_adress": row.get("mac_adress"),
        "ip_adress": row.get("ip_adress"),
        "date": str(date_creation) if date_creation else None,
        "ram_total": ram_total,
        "ram_total_label": format_bytes(ram_total),
        "disk_total": disk_total,
        "disk_total_label": format_bytes(disk_total),
        "disk_free": disk_free,
        "disk_free_label": format_bytes(disk_free),
        "disk_used": disk_used,
        "disk_used_label": format_bytes(disk_used),
        "disk_model": row.get("disk_model"),
        "disk_type": row.get("disk_type"),
        "cpu_model": row.get("cpu_model"),
        "cpu_freq_max": row.get("cpu_freq_max"),
        "cpu_freq_max_label": format_frequency(row.get("cpu_freq_max")),
        "cpu_architecture": row.get("cpu_architecture"),
        "id_utilisateur": row.get("id_utilisateur"),
        "status": row.get("status") or "UNKNOWN",
        "utilisateur_email": row.get("utilisateur_email") or "N/A",
        "utilisateurs_recents": row.get("utilisateurs_recents") or [],
        "filiale": row.get("filiale"),
    }


def _fetch_devices_page(page=1, page_size=10, id_filiale=None, filiale=None,
                        statut=None, type_appareil=None, recherche=None,
                        datetime_from=None, datetime_to=None):
    connexion = get_connection()
    if connexion is None:
        return build_page([], 0, page, page_size)
    try:
        cur = connexion.cursor()
        rows = find_devices_paginated(
            cur, page, page_size, id_filiale, filiale,
            statut, type_appareil, recherche, datetime_from, datetime_to
        )
        total = rows[0]["total"] if rows else 0
        items = [_serialize_device_row(row) for row in rows]
        cur.close()
        return build_page(items, total, page, page_size)
    finally:
        close_connection(connexion)


def _devices_cache_key(page, page_size, id_filiale, filiale, statut,
                       type_appareil, recherche, datetime_from, datetime_to):
    return (
        f"devices:{page}:{page_size}:{id_filiale}:{filiale}:"
        f"{statut}:{type_appareil}:{recherche}:{datetime_from}:{datetime_to}"
    )


def getDevicesPage(page=1, page_size=10, id_filiale=None, filiale=None,
                   statut=None, type_appareil=None, recherche=None,
                   datetime_from=None, datetime_to=None):
    cle = _devices_cache_key(
        page, page_size, id_filiale, filiale, statut, type_appareil,
        recherche, datetime_from, datetime_to
    )
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    resultat = _fetch_devices_page(
        page, page_size, id_filiale, filiale, statut, type_appareil,
        recherche, datetime_from, datetime_to
    )
    return cache_set(cle, resultat)
        
# if __name__ == "__main__":
#     connexion = get_connection()
#     cur = connexion.cursor()
#     # device = recherche_multicritere(cur,'digital.salamander@taloumis.mg')
#     # device = getDeviceDetail(2)
#     print(device)
