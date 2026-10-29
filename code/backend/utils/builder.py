from backend.fonction.metier.repository.devices import (
    get_filiale_by_device,
    _get_device_cpu_info,
    _get_last_disk_info,
    _get_recent_users,
    get_type_appareil_by_id,
    get_utilisateurs_by_device,
)
from backend.fonction.metier.repository.statut import get_status_actuel_device
from backend.utils.format_valeur import format_bytes, format_frequency


def _build_device_response(cur, d):
    if not d:
        return None

    device_id = d[0]
    status = get_status_actuel_device(cur, device_id)
    utilisateurs = get_utilisateurs_by_device(cur, device_id)
    id_utilisateur = utilisateurs[0][0] if utilisateurs else None
    utilisateur_email = utilisateurs[0][1] if utilisateurs else "N/A"

    filiale_res = get_filiale_by_device(cur, device_id)
    filiale_nom = filiale_res[1] if filiale_res and filiale_res[1] else None

    type_appareil_res = get_type_appareil_by_id(cur, d[4]) if d[4] else None
    type_appareil_nom = type_appareil_res[1] if type_appareil_res else None

    recent_users = _get_recent_users(cur, device_id)
    cpu_info = _get_device_cpu_info(cur, device_id)
    disk_info = _get_last_disk_info(cur, device_id)

    ram_total = d[10] if len(d) > 10 else None
    disk_total = disk_info[0] if disk_info else None
    disk_free = disk_info[2] if disk_info and len(disk_info) > 2 else None
    disk_used = disk_info[3] if disk_info and len(disk_info) > 3 else None

    disk_total_label = disk_info[1] if disk_info and disk_info[1] is not None else format_bytes(disk_total)
    disk_free_label = format_bytes(disk_free) if disk_free is not None else None
    disk_used_label = format_bytes(disk_used) if disk_used is not None else None

    if disk_free is None and disk_total is not None and disk_used is not None:
        disk_free = max(disk_total - disk_used, 0)
        disk_free_label = format_bytes(disk_free)
    if disk_used is None and disk_total is not None and disk_free is not None:
        disk_used = max(disk_total - disk_free, 0)
        disk_used_label = format_bytes(disk_used)

    return {
        "id": device_id,
        "id_device": d[1],
        "serial_number": d[2],
        "modele": d[3],
        "id_type_appareil": d[4],
        "type_appareil": type_appareil_nom,
        "chromeos_version": d[5],
        "chrome_version": d[6],
        "mac_adress": d[7],
        "ip_adress": d[8],
        "date": str(d[9]) if d[9] else None,
        "id_utilisateur": id_utilisateur,
        "status": status,
        "utilisateur_email": utilisateur_email,
        "utilisateurs_recents": recent_users,
        "filiale": filiale_nom,
        "ram_total": ram_total,
        "ram_total_label": format_bytes(ram_total),
        "disk_total": disk_total,
        "disk_total_label": disk_total_label,
        "disk_free": disk_free,
        "disk_free_label": disk_free_label,
        "disk_used": disk_used,
        "disk_used_label": disk_used_label,
        "disk_model": disk_info[4] if disk_info else None,
        "disk_type": disk_info[5] if disk_info else None,
        "cpu_model": cpu_info[0] if cpu_info else None,
        "cpu_freq_max": cpu_info[1] if cpu_info else None,
        "cpu_freq_max_label": format_frequency(cpu_info[1]) if cpu_info and cpu_info[1] is not None else None,
        "cpu_architecture": cpu_info[2] if cpu_info else None,
    }
    
    
def _serialize_alerte(row):
    return {
        "id": row[0],
        "type": row[1],
        "date": row[2],
    }


def _serialize_alerte_resume(row):
    return {
        "id": row[0],
        "id_device": row[1],
        "serial_number": row[2],
        "type": row[3],
        "message": row[4],
        "date": row[5],
        "utilisateur_recent": row[6],
    }

def _serialize_device_alerte(row):
    return {
        "id": row[0],
        "id_device": row[1],
        "serial_number": row[2],
        "type": row[3],
        "message": row[4],
        "date": row[5],
        "utilisateur_recent": row[6],
    }
    
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
