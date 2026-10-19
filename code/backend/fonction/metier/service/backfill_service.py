import json
from datetime import datetime, timezone

from backend.fonction.metier.repository.cpu.cpu import get_or_create_cpu
from backend.fonction.metier.repository.cpu.device_cpu import insert_cpu_device
from backend.fonction.metier.repository.rapport import get_rapport_by_device, get_rapport_by_device_and_type
from backend.fonction.metier.repository.rapport.type_rapport import get_id_by_type_name
from backend.fonction.metier.repository.ram.ram import insert_into_device_ram
from backend.fonction.metier.repository.disk.disk import get_or_create_disk
from backend.fonction.metier.repository.disk.disk_device import insert_disk_device
from backend.fonction.metier.repository.evenement import create_evenement_device
from backend.utils.format_valeur import _to_int, format_bytes
from backend.utils.format_date import parse_date_safe


def _to_aware_datetime(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    parsed = parse_date_safe(value)
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _should_skip_historical_insert(cur, table_name, id_device, report_time, force=False):
    if force:
        return False

    parsed = _to_aware_datetime(report_time)
    if parsed is None:
        return False

    if parsed.date() >= datetime.now(timezone.utc).date():
        return False

    cur.execute(
        f"""
        SELECT 1
        FROM {table_name}
        WHERE id_device = %s AND date = %s
        LIMIT 1
        """,
        (id_device, parsed),
    )
    return cur.fetchone() is not None


def _resolve_cpu_id_for_device(cur, id_device, payload=None):
    cur.execute(
        """
        SELECT id_cpu
        FROM t_device_cpu
        WHERE id_device = %s
        ORDER BY date DESC
        LIMIT 1
        """,
        (id_device,),
    )
    row = cur.fetchone()
    if row and row[0] is not None:
        return row[0]

    cpu_data = payload or {}
    cpu_model = cpu_data.get("cpuModel") or cpu_data.get("model") or "UNKNOWN"
    cpu_architecture = cpu_data.get("architecture") or cpu_data.get("architectureName") or "UNKNOWN"
    frequency = cpu_data.get("maxClockSpeedKhz") or cpu_data.get("maxClockSpeed") or cpu_data.get("frequencyKhz")
    return get_or_create_cpu(cur, cpu_model, _to_int(frequency), cpu_architecture)


def _coerce_historic_payload(raw_value):
    if isinstance(raw_value, str):
        try:
            raw_value = json.loads(raw_value)
        except (TypeError, ValueError):
            return {}
    return raw_value if isinstance(raw_value, dict) else {}


def _resolve_historic_date(raw_rows, fallback_date=None):
    fallback_date = parse_date_safe(fallback_date) or datetime.now(timezone.utc)
    fallback_date = _to_aware_datetime(fallback_date)

    if not raw_rows:
        return fallback_date

    for raw_row in raw_rows:
        payload = _coerce_historic_payload(raw_row[4] if len(raw_row) > 4 else {})
        report_time = payload.get("reportTime")
        if report_time is None and len(raw_row) > 3:
            report_time = raw_row[3]

        parsed = parse_date_safe(report_time)
        if parsed is not None:
            return _to_aware_datetime(parsed)

    return fallback_date


def _extract_payload(raw_value):
    if raw_value is None:
        return {}
    if isinstance(raw_value, str):
        try:
            raw_value = json.loads(raw_value)
        except (TypeError, ValueError):
            return {}
    return raw_value if isinstance(raw_value, dict) else {}


def _try_insert_ram_snapshot(cur, id_device, payload, report_time):
    if not payload:
        return False

    ram_total = _to_int(
        payload.get("totalRamBytes")
        or payload.get("totalMemoryBytes")
        or payload.get("ramTotalBytes")
    )
    ram_libre = _to_int(
        payload.get("systemRamFreeBytes")
        or payload.get("freeRamBytes")
        or payload.get("availableRamBytes")
        or payload.get("ramFreeBytes")
    )

    if ram_total is None and ram_libre is None:
        return False

    if ram_total is not None and ram_libre is not None:
        ram_utiliser = max(ram_total - ram_libre, 0)
    else:
        ram_utiliser = None

    if _should_skip_historical_insert(cur, "t_device_ram", id_device, report_time):
        return False

    insert_into_device_ram(cur, id_device, ram_total, ram_utiliser, ram_libre, report_time)
    return True


def _try_insert_cpu_snapshot(cur, id_device, payload, report_time):
    if not payload:
        return False

    cpu_utilisation_pct = payload.get("cpuUtilizationPct")
    if cpu_utilisation_pct is None:
        return False

    if _should_skip_historical_insert(cur, "t_device_cpu", id_device, report_time):
        return False

    cpu_total_val = 100
    cpu_utiliser_val = float(cpu_utilisation_pct)
    cpu_libre_val = max(int(round(cpu_total_val - cpu_utiliser_val)), 0)
    cpu_id = _resolve_cpu_id_for_device(cur, id_device, payload)

    insert_cpu_device(cur, id_device, cpu_id, cpu_utiliser_val, cpu_total_val, cpu_libre_val, report_time)
    return True


# def _try_insert_disk_snapshot(cur, id_device, payload, report_time):
#     if not payload:
#         return False

#     disks = payload.get("disk") or payload.get("disks") or []
#     disk = disks[0] if isinstance(disks, list) and disks else {}

#     disk_model = disk.get("model") or disk.get("name") or "UNKNOWN"
#     disk_type = disk.get("type") or disk.get("diskType") or "UNKNOWN"

#     # --- Récupération du volume principal ---
#     volumes = disk.get("volume") or disk.get("volumes") or []
#     volume = volumes[0] if isinstance(volumes, list) and volumes else {}

#     # Google renvoie les tailles dans volume[]
#     disk_size = _to_int(
#         volume.get("storageTotalBytes")
#         or disk.get("sizeBytes")
#         or disk.get("totalBytes")
#         or payload.get("totalDiskBytes")
#         or payload.get("totalStorageBytes")
#     )
#     disk_available = _to_int(
#         volume.get("storageFreeBytes")
#         or disk.get("freeBytes")
#         or payload.get("availableDiskBytes")
#         or payload.get("freeDiskBytes")
#     )
#     disk_used = _to_int(
#         volume.get("storageUsedBytes")
#         or disk.get("usedBytes")
#     )

#     # Si on n'a pas au moins une info exploitable, on n'insère RIEN
#     if disk_size is None and disk_available is None and disk_used is None:
#         return False

#     # Si on n'a que le total et rien d'autre → inutile d'insérer, données trompeuses
#     if disk_available is None and disk_used is None:
#         # Option A : retourner False (recommandé)
#         return False
#         # Option B (décommenter si tu veux vraiment garder le total seul) :
#         # disk_available = None
#         # disk_used = None

#     disk_id = get_or_create_disk(cur, disk_model, disk_type)
#     if not disk_id:
#         return False

#     total_reel = disk_size if disk_size is not None else 0
#     total_formater = format_bytes(total_reel)

#     # Logique corrigée : ne déduit plus "utiliser = 0" par défaut
#     if disk_available is not None:
#         disponible = max(disk_available, 0)
#     elif disk_used is not None and disk_size is not None:
#         disponible = max(disk_size - disk_used, 0)
#     else:
#         disponible = None      # ← au lieu de total_reel

#     if disk_used is not None:
#         utiliser = max(disk_used, 0)
#     elif disponible is not None and disk_size is not None:
#         utiliser = max(disk_size - disponible, 0)
#     else:
#         utiliser = None        # ← au lieu de 0

#     total_utiliser_formater = format_bytes(utiliser) if utiliser is not None else None
#     disponible_formater = format_bytes(disponible) if disponible is not None else None

#     insert_disk_device(
#         cur, id_device, disk_id,
#         disponible, disponible_formater,
#         total_reel, total_formater,
#         utiliser, total_utiliser_formater,
#         report_time,
#     )
#     return True


def backfill_device_history_from_rapport(cur, id_device):
    """
    Recharge manuel des anciennes valeurs CPU/RAM depuis t_rapport_device pour un device donné.
    Ce service n'est pas déclenché automatiquement dans la synchronisation courante.
    Il sert à reconstituer l'historique de manière explicite et sécurisée.
    Les lignes historiques antérieures à aujourd'hui ne sont pas réinsérées si elles existent déjà.
    """
    rapports = get_rapport_by_device(cur, id_device)
    if not rapports:
        return 0

    inserted = 0

    for row in rapports:
        if len(row) < 5:
            continue

        raw_record = row[4]
        payload = _extract_payload(raw_record)
        if not payload:
            continue

        report_time = payload.get("reportTime") or row[3]
        parsed_time = _to_aware_datetime(report_time)
        if parsed_time is None:
            continue

        if parsed_time.date() < datetime.now(timezone.utc).date():
            if _should_skip_historical_insert(cur, "t_device_ram", id_device, parsed_time):
                pass

        if _try_insert_ram_snapshot(cur, id_device, payload, parsed_time):
            inserted += 1

        if _try_insert_cpu_snapshot(cur, id_device, payload, parsed_time):
            inserted += 1

    # --- Backfill DISK depuis les rapports STORAGE_STATUS ---
    id_type_storage = get_id_by_type_name(cur, "STORAGE_STATUS")
    if id_type_storage is not None:
        rapports_disk = get_rapport_by_device_and_type(cur, id_device, id_type_storage)
        for row_disk in rapports_disk:
            raw_disk = row_disk.get("donnees") if isinstance(row_disk, dict) else (row_disk[4] if len(row_disk) > 4 else None)
            disk_payload = _extract_payload(raw_disk)
            if not disk_payload:
                continue

            disk_report_time = disk_payload.get("reportTime") or (row_disk.get("report_time") if isinstance(row_disk, dict) else (row_disk[3] if len(row_disk) > 3 else None))
            parsed_disk_time = _to_aware_datetime(disk_report_time)
            if parsed_disk_time is None:
                continue

            # if _try_insert_disk_snapshot(cur, id_device, disk_payload, parsed_disk_time):
            #     inserted += 1

    return inserted


def backfill_all_devices_history(cur, device_ids=None):
    if device_ids is None:
        cur.execute("SELECT id FROM t_device ORDER BY id ASC")
        device_ids = [row[0] for row in cur.fetchall()]

    total = 0
    for device_id in device_ids:
        total += backfill_device_history_from_rapport(cur, device_id)
    return total


def dedup_evenement_device(cur):
    """
    Supprime les doublons dans t_evenement_device tout en conservant
    un exemplaire unique de chaque evenement (id_device, id_type_evenement, date_evenement).
    Etapes :
      1. Sauvegarde les evenements uniques dans une table temporaire
      2. Vide t_evenement_device
      3. Reinstere les evenements uniques
    Ainsi meme apres suppression, les evenements sont recuperes.
    """
    # 1) Sauvegarder les evenements uniques (garder le plus recent par groupe)
    cur.execute("""
        CREATE TEMP TABLE _tmp_evenement_backup AS
        SELECT DISTINCT ON (id_device, id_type_evenement, date_evenement)
            id_device, id_type_evenement, date_evenement, details
        FROM t_evenement_device
        ORDER BY id_device, id_type_evenement, date_evenement, id DESC
    """)
    cur.execute("SELECT COUNT(*) FROM _tmp_evenement_backup")
    nb_uniques = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM t_evenement_device")
    nb_avant = cur.fetchone()[0]

    # 2) Vider la table originale
    cur.execute("TRUNCATE TABLE t_evenement_device RESTART IDENTITY")

    # 3) Reinsterer les evenements uniques
    cur.execute("""
        INSERT INTO t_evenement_device (id_device, id_type_evenement, date_evenement, details)
        SELECT id_device, id_type_evenement, date_evenement, details
        FROM _tmp_evenement_backup
        ORDER BY date_evenement
    """)

    # 4) Nettoyer la table temporaire
    cur.execute("DROP TABLE _tmp_evenement_backup")

    # 5) Ajouter la contrainte UNIQUE si elle n'existe pas encore
    cur.execute("""
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_evenement_device'
    """)
    if not cur.fetchone():
        cur.execute("""
            ALTER TABLE t_evenement_device
            ADD CONSTRAINT uq_evenement_device UNIQUE (id_device, id_type_evenement, date_evenement)
        """)
        print("  [EVENEMENT] Contrainte UNIQUE (id_device, id_type_evenement, date_evenement) ajoutee")

    nb_supprimes = nb_avant - nb_uniques
    print(f"  [EVENEMENT] {nb_avant} lignes -> {nb_uniques} uniques ({nb_supprimes} doublons supprimes)")
    return nb_uniques


def main():
    print("[backfill_service] Ce service est destine au backfill historique depuis t_rapport_device.")


if __name__ == "__main__":
    main()
