from backend.utils.format_valeur import format_bytes, format_frequency


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
        "id_status": row.get("id_status"),
        "utilisateur_email": row.get("utilisateur_email") or "N/A",
        "utilisateurs_recents": row.get("utilisateurs_recents") or [],
        "filiale": row.get("filiale"),
    }
