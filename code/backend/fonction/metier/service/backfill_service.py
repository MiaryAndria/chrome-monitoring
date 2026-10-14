import json
from datetime import datetime, timezone

from backend.fonction.metier.repository.cpu.cpu import get_or_create_cpu
from backend.fonction.metier.repository.cpu.device_cpu import insert_cpu_device
from backend.fonction.metier.repository.rapport import get_rapport_by_device
from backend.fonction.metier.repository.ram.ram import insert_into_device_ram
from backend.utils.format_valeur import _to_int
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

    return inserted


def backfill_all_devices_history(cur, device_ids=None):
    if device_ids is None:
        cur.execute("SELECT id FROM t_device ORDER BY id ASC")
        device_ids = [row[0] for row in cur.fetchall()]

    total = 0
    for device_id in device_ids:
        total += backfill_device_history_from_rapport(cur, device_id)
    return total


def main():
    print("[backfill_service] Ce service est destiné au backfill historique depuis t_rapport_device.")


if __name__ == "__main__":
    main()
