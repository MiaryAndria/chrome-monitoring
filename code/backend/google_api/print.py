from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from backend.utils.datetime_tools import parse_dt


# ============================================================================
# Imprimantes USB / détection
# ============================================================================

PRINTER_CLASS = 7

SCANNER_KEYWORDS = ["canoscan", "lidescan", "lide ", "lide", "scanjet", "scansnap"]
PRINTER_STRONG_KEYWORDS = [
    "printer", "deskjet", "laserjet", "officejet", "envy", "pagewide",
    "pixma", "ecotank", "workforce", "imageclass", "mfc-", "dcp-", "hl-",
    "p-touch", "lq-", "l3110", "l3150", "l3250", "l3210", "l4260", "l5290",
    "lexmark", "xerox", "kyocera", "ricoh", "zebra", "dymo", "bixolon",
    "printer-80", "usb printer port",
]
NON_PRINTER_KEYWORDS = [
    "mouse", "keyboard", "root hub", " hub", "camera", "webcam",
    "headset", "audio", "microphone", "mic ", "storage", "disk",
    "flash", "mtp", "android", "phone", "galaxy", "iphone",
    "touchpad", "gamepad", "joystick", "barcode", "reader",
    "ethernet", "wireless", "bluetooth", "receiver", "motorola", "moto g",
]


def _text(usb):
    return f"{usb.get('vendor') or ''} {usb.get('name') or ''}".lower()


def is_printer_peripheral(usb, include_scanners=False):
    if not usb:
        return False

    name = (usb.get("name") or "").lower().strip()
    text = _text(usb)
    if not name:
        return False

    if any(kw in text for kw in NON_PRINTER_KEYWORDS):
        return False

    if not include_scanners and any(kw in name for kw in SCANNER_KEYWORDS):
        return False

    class_codes = usb.get("classCodes") or [usb.get("classId")]
    if PRINTER_CLASS in class_codes:
        return True

    return any(kw in text for kw in PRINTER_STRONG_KEYWORDS)


def extract_printers_from_telemetry(telemetry_devices):
    """Extrait toutes les imprimantes USB vues dans la télémétrie."""
    printers = []

    for tel in telemetry_devices:
        device_id = tel.get("deviceId", "?")
        serial = tel.get("serialNumber", "?")
        org_unit_id = tel.get("orgUnitId", "?")

        for report in tel.get("peripheralsReport", []) or []:
            report_time = report.get("reportTime")
            for usb in report.get("usbPeripheralReport", []) or []:
                if not is_printer_peripheral(usb):
                    continue
                printers.append({
                    "deviceId": device_id,
                    "deviceSerialNumber": serial,
                    "orgUnitId": org_unit_id,
                    "vendor": usb.get("vendor", "Inconnu"),
                    "model": usb.get("name", "Inconnu"),
                    "vid": usb.get("vid"),
                    "pid": usb.get("pid"),
                    "connectionType": "USB",
                    "lastSeen": report_time,
                })

    seen = {}
    for p in printers:
        key = (p["deviceId"], p["vid"], p["pid"], p["model"])
        existing = seen.get(key)
        if not existing or (p["lastSeen"] and p["lastSeen"] > existing["lastSeen"]):
            seen[key] = p

    return list(seen.values())


def build_device_printers_index(detected_printers):
    """Index deviceId -> liste d'imprimantes USB vues sur ce device."""
    index = defaultdict(dict)

    for p in detected_printers:
        dev_id = p.get("deviceId")
        if not dev_id:
            continue
        key = (p.get("vid"), p.get("pid"), p.get("model"))
        existing = index[dev_id].get(key)
        if not existing or (p.get("lastSeen") and p["lastSeen"] > existing.get("lastSeen", "")):
            index[dev_id][key] = p

    return {dev_id: list(printers.values()) for dev_id, printers in index.items()}


# ============================================================================
# Audit logs d'impression / matching
# ============================================================================

MAX_DEVICES_PER_USER = 5
OLD_PRINT_DAYS = 60
MAX_DELTA_HOURS = 48


def get_print_audit_logs(credentials, days=90):
    """Événements d'impression Google Workspace (Docs, Sheets, Slides, Drive)."""
    try:
        from googleapiclient.discovery import build
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "googleapiclient is required to fetch print audit logs."
        ) from exc

    service = build("admin", "reports_v1", credentials=credentials, cache_discovery=False)
    start = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    all_events = []
    page_token = None

    while True:
        response = service.activities().list(
            userKey="all",
            applicationName="drive",
            eventName="print",
            startTime=start,
            maxResults=1000,
            pageToken=page_token,
        ).execute()

        for item in response.get("items", []):
            for ev in item.get("events", []):
                if ev.get("name") != "print":
                    continue
                all_events.append({
                    "user": item.get("actor", {}).get("email"),
                    "time": item.get("id", {}).get("time"),
                    "ip": item.get("ipAddress"),
                    "documentId": ev.get("parameters", [{}])[0].get("value") if ev.get("parameters") else None,
                    "documentTitle": next((p["value"] for p in ev.get("parameters", []) if p.get("name") == "doc_title"), None),
                })

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return all_events


def build_email_index(devices):
    """Construit l'index email -> liste de devices où l'utilisateur est apparu."""
    email_to_devices = defaultdict(list)

    for d in devices:
        device_meta = {
            "deviceId": d.get("deviceId"),
            "serialNumber": d.get("serialNumber"),
            "model": d.get("model"),
            "orgUnitPath": d.get("orgUnitPath"),
            "lastSync": d.get("lastSync"),
            "status": d.get("status"),
            "ipAddress": None,
            "wanIpAddress": None,
        }

        nets = d.get("lastKnownNetwork") or []
        if nets:
            device_meta["ipAddress"] = nets[0].get("ipAddress")
            device_meta["wanIpAddress"] = nets[0].get("wanIpAddress")

        for u in d.get("recentUsers", []):
            email = (u.get("email") or "").lower().strip()
            if email:
                email_to_devices[email].append(device_meta)

    return email_to_devices


def extract_managed_domains(devices):
    """Extrait les domaines email managés depuis les devices."""
    domains = set()
    for d in devices:
        for u in d.get("recentUsers", []):
            email = u.get("email")
            if email and "@" in email:
                domains.add(email.split("@", 1)[1].lower())
        annotated = d.get("annotatedUser")
        if annotated and "@" in annotated:
            domains.add(annotated.split("@", 1)[1].lower())
    return domains


def build_telemetry_index(telemetry):
    """Index deviceId -> { heartbeats: [dt], network_reports: [(dt, lanIP)] }."""
    idx = {}
    for t in telemetry:
        dev_id = t.get("deviceId")
        if not dev_id:
            continue

        heartbeats = []
        for h in t.get("heartbeatStatusReport", []) or []:
            dt = parse_dt(h.get("reportTime"))
            if dt:
                heartbeats.append(dt)

        net_reports = []
        for n in t.get("networkStatusReport", []) or []:
            dt = parse_dt(n.get("reportTime"))
            if dt:
                net_reports.append((dt, n.get("lanIpAddress")))

        idx[dev_id] = {
            "heartbeats": sorted(heartbeats),
            "network_reports": sorted(net_reports, key=lambda x: x[0]),
        }
    return idx


def match_print_to_devices(print_log, email_index, telemetry_index, managed_domains, max_delta_hours=MAX_DELTA_HOURS):
    """Retourne (candidats, flags) pour associer une impression à un device."""
    user = (print_log.get("user") or "").lower().strip()
    ip = print_log.get("ip")
    t = parse_dt(print_log.get("time"))
    now = datetime.now(timezone.utc)

    flags = {
        "unmanaged_user": False,
        "unmatched_user": False,
        "no_document_id": not print_log.get("documentId"),
    }

    domain = user.split("@", 1)[1] if "@" in user else ""
    if domain and domain not in managed_domains:
        flags["unmanaged_user"] = True

    matches = email_index.get(user, [])
    if not matches:
        flags["unmatched_user"] = True
        return [], flags

    age_days = (now - t).days if t else 0
    old_print = age_days > OLD_PRINT_DAYS

    candidates = []
    for dev in matches:
        score = 50
        reason = ["email OK"]

        if ip and dev.get("wanIpAddress") == ip:
            if old_print:
                score += 5
                reason.append(f"WAN IP OK (impression >{OLD_PRINT_DAYS}j, poids réduit)")
            else:
                score += 30
                reason.append("WAN IP OK")

        if t and dev["deviceId"] in telemetry_index:
            tel = telemetry_index[dev["deviceId"]]
            hbs_before = [h for h in tel["heartbeats"] if h <= t]
            if hbs_before:
                delta_h = (t - max(hbs_before)).total_seconds() / 3600
                if delta_h <= max_delta_hours:
                    score += 20
                    reason.append(f"actif il y a {delta_h:.1f}h")

            for n_dt, n_ip in reversed(tel["network_reports"]):
                if n_dt <= t:
                    if n_ip and n_ip == ip:
                        score += 10
                        reason.append("LAN récent = IP log")
                    break

        candidates.append({
            "device": dev,
            "score": score,
            "reason": " + ".join(reason),
        })

    candidates.sort(key=lambda c: c["score"], reverse=True)
    return candidates, flags


def enrich_print_logs(print_logs, devices, telemetry, detected_printers):
    """Enrichit chaque log d'impression avec le device matché et les imprimantes associées."""
    email_index = build_email_index(devices)
    telemetry_index = build_telemetry_index(telemetry)
    managed_domains = extract_managed_domains(devices)
    device_printers = build_device_printers_index(detected_printers)

    enriched = []
    unmatched_users = defaultdict(lambda: {
        "count": 0,
        "documents": [],
        "first_seen": None,
        "last_seen": None,
    })

    stats = {
        "total": len(print_logs),
        "matched": 0,
        "matched_confident": 0,
        "ambiguous": 0,
        "unmatched": 0,
        "no_device": 0,
        "unmanaged_users": 0,
        "no_document_id": 0,
        "old_prints": 0,
        "with_printer_single": 0,
        "with_printer_multiple": 0,
        "no_printer_on_device": 0,
    }

    for log in print_logs:
        cands, flags = match_print_to_devices(log, email_index, telemetry_index, managed_domains)
        best = cands[0] if cands and cands[0]["device"] else None

        device_candidates = [c for c in cands if c["device"]]
        many_devices = len(device_candidates) > MAX_DEVICES_PER_USER
        ambiguous = (len(device_candidates) > 1) or many_devices

        if flags["unmatched_user"]:
            user = (log.get("user") or "").lower().strip()
            entry = unmatched_users[user]
            entry["count"] += 1
            entry["documents"].append({
                "time": log.get("time"),
                "documentTitle": log.get("documentTitle"),
                "ip": log.get("ip"),
            })
            t_str = log.get("time")
            if t_str:
                if entry["first_seen"] is None or t_str < entry["first_seen"]:
                    entry["first_seen"] = t_str
                if entry["last_seen"] is None or t_str > entry["last_seen"]:
                    entry["last_seen"] = t_str
            entry["unmanaged_user"] = flags["unmanaged_user"]

        attached_printers = []
        likely_printer = None
        printer_confidence = "none"

        if best and best["device"]:
            dev_id = best["device"]["deviceId"]
            attached_printers = device_printers.get(dev_id, [])

            if len(attached_printers) == 1:
                likely_printer = attached_printers[0]
                printer_confidence = "single"
                stats["with_printer_single"] += 1
            elif len(attached_printers) > 1:
                printer_confidence = "multiple"
                stats["with_printer_multiple"] += 1
            else:
                stats["no_printer_on_device"] += 1

        entry = {
            "user": log.get("user"),
            "time": log.get("time"),
            "ip": log.get("ip"),
            "documentId": log.get("documentId"),
            "documentTitle": log.get("documentTitle"),
            "matched_device": best["device"] if best else None,
            "match_score": best["score"] if best else 0,
            "match_reason": best["reason"] if best else "non matché",
            "attached_printers": attached_printers,
            "likely_printer": likely_printer,
            "printer_confidence": printer_confidence,
            "flags": {
                "ambiguous": ambiguous,
                "many_devices": many_devices,
                "unmanaged_user": flags["unmanaged_user"],
                "unmatched_user": flags["unmatched_user"],
                "no_document_id": flags["no_document_id"],
            },
            "all_candidates": [
                {
                    "deviceId": c["device"]["deviceId"] if c["device"] else None,
                    "score": c["score"],
                    "reason": c["reason"],
                }
                for c in cands
            ],
        }
        enriched.append(entry)

        if flags["no_document_id"]:
            stats["no_document_id"] += 1
        if flags["unmanaged_user"]:
            stats["unmanaged_users"] += 1
        if best and (t := parse_dt(log.get("time"))) and (datetime.now(timezone.utc) - t).days > OLD_PRINT_DAYS:
            stats["old_prints"] += 1

        if not best:
            stats["unmatched"] += 1
            if flags["unmatched_user"]:
                stats["no_device"] += 1
        else:
            stats["matched"] += 1
            if best["score"] >= 80:
                stats["matched_confident"] += 1
            if ambiguous:
                stats["ambiguous"] += 1

    return enriched, dict(unmatched_users), stats


__all__ = [
    "MAX_DEVICES_PER_USER",
    "OLD_PRINT_DAYS",
    "MAX_DELTA_HOURS",
    "SCANNER_KEYWORDS",
    "PRINTER_STRONG_KEYWORDS",
    "NON_PRINTER_KEYWORDS",
    "PRINTER_CLASS",
    "is_printer_peripheral",
    "extract_printers_from_telemetry",
    "build_device_printers_index",
    "get_print_audit_logs",
    "parse_dt",
    "build_email_index",
    "extract_managed_domains",
    "build_telemetry_index",
    "match_print_to_devices",
    "enrich_print_logs",
]
