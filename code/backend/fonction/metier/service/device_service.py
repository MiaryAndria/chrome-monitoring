from backend.fonction.conn.transaction import lecture
from backend.fonction.metier.repository.devices import (
    get_device_detail,
    get_liste_modele,
    get_all_device_stats,
    find_devices_paginated,
)
from backend.utils.format_valeur import format_bytes, format_frequency
from backend.utils.pagination import build_page
from backend.core.cache import cache_get, cache_set


def getDeviceDetail(id):
    with lecture() as cur:
        if cur is None:
            return None
        row = get_device_detail(cur, id)
        if row is None:
            return None

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
            "id_status": row.get("id_status"),
            "utilisateur_email": row.get("utilisateur_email") or "N/A",
            "utilisateurs_recents": row.get("utilisateurs_recents") or [],
            "filiale": row.get("filiale"),
        }


def _fetch_devices_page(page=1, page_size=10, id_filiale=None, filiale=None,
                        id_statut=None, statut=None, type_appareil=None, recherche=None,
                        datetime_from=None, datetime_to=None,modele=None,utilisateur_recent=None):
    with lecture() as cur:
        if cur is None:
            return build_page([], 0, page, page_size)
        rows, total = find_devices_paginated(
            cur, page, page_size,
            id_filiale=id_filiale, filiale=filiale, id_statut=id_statut, statut=statut,
            type_appareil=type_appareil, recherche=recherche,
            datetime_from=datetime_from, datetime_to=datetime_to,
            modele=modele, utilisateur_recent=utilisateur_recent
        )

        items = []
        for row in rows:
            ram_total = row.get("ram_total")
            disk_total = row.get("disk_total")
            disk_free = row.get("disk_free")
            disk_used = row.get("disk_used")

            if disk_free is None and disk_total is not None and disk_used is not None:
                disk_free = max(disk_total - disk_used, 0)
            if disk_used is None and disk_total is not None and disk_free is not None:
                disk_used = max(disk_total - disk_free, 0)

            date_creation = row.get("date")

            items.append({
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
                "id_status": row.get("id_status"),
                "utilisateur_email": row.get("utilisateur_email") or "N/A",
                "utilisateurs_recents": row.get("utilisateurs_recents") or [],
                "filiale": row.get("filiale"),
            })

        return build_page(items, total, page, page_size)


def _devices_cache_key(page, page_size, id_filiale, filiale, id_statut, statut,
                       type_appareil, recherche, datetime_from, datetime_to,modele,utilisateur_recent):
    return (
        f"devices:{page}:{page_size}:{id_filiale}:{filiale}:{utilisateur_recent}:"
        f"{id_statut}:{statut}:{type_appareil}:{recherche}:{datetime_from}:{datetime_to}:{modele}"
    )


def getDevicesPage(page=1, page_size=10, id_filiale=None, filiale=None,
                   id_statut=None, statut=None, type_appareil=None, recherche=None,
                   datetime_from=None, datetime_to=None, modele=None,utilisateur_recent=None):
    cle = _devices_cache_key(
        page, page_size, id_filiale, filiale, id_statut, statut, type_appareil,
        recherche, datetime_from, datetime_to, modele,utilisateur_recent
    )
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    resultat = _fetch_devices_page(
        page, page_size, id_filiale, filiale, id_statut, statut, type_appareil,
        recherche, datetime_from, datetime_to, modele,utilisateur_recent
    )
    return cache_set(cle, resultat)


MODELES_CACHE_KEY = "devices:modeles"
MODELES_CACHE_TTL = 300

DEVICE_STATS_CACHE_KEY = "devices:stats:all"
DEVICE_STATS_CACHE_TTL = 60


def get_device_stats():
    valeur = cache_get(DEVICE_STATS_CACHE_KEY)
    if valeur is not None:
        return valeur

    with lecture() as cur:
        if cur is None:
            return {"total": 0, "actifs": 0}
        resultat = get_all_device_stats(cur)
        return cache_set(DEVICE_STATS_CACHE_KEY, resultat, DEVICE_STATS_CACHE_TTL)


def get_modeles():
    valeur = cache_get(MODELES_CACHE_KEY)
    if valeur is not None:
        return valeur

    with lecture() as cur:
        if cur is None:
            return []
        rows = get_liste_modele(cur)
        return cache_set(MODELES_CACHE_KEY, rows, MODELES_CACHE_TTL)
