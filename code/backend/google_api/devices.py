import os
from pathlib import Path
from dotenv import load_dotenv
def load_dotenv(*args, **kwargs):
        return False
from googleapiclient.discovery import build
from backend.utils.save_to_file import save
from backend.utils.save_to_json import save_to_json
from backend.utils.format_date import format_date
from backend.utils.format_org import format_org_unit
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from backend.utils.get_credential import get_credentials

load_dotenv()

# ==============================================================
# CONFIGURATION
# ==============================================================

BASE_DIR = Path(__file__).resolve().parents[3]
_token_env_path = os.getenv("GOOGLE_TOKEN_PATH", "credential/token.json")
_candidate_path = (
    Path(_token_env_path) if Path(_token_env_path).is_absolute()
    else (BASE_DIR / _token_env_path).resolve()
)

if not _candidate_path.exists():
    _fallback = (BASE_DIR / "credential" / "token.json").resolve()
    TOKEN_FILE = _fallback if _fallback.exists() else _candidate_path
else:
    TOKEN_FILE = _candidate_path

OUTPUT_DIR = BASE_DIR / "output"

SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly",
    "https://www.googleapis.com/auth/chrome.management.telemetry.readonly",
    "https://www.googleapis.com/auth/chrome.management.reports.readonly",
    "https://www.googleapis.com/auth/admin.directory.customer.readonly",
    "https://www.googleapis.com/auth/admin.directory.user.readonly",
    "https://www.googleapis.com/auth/admin.reports.audit.readonly",
    "https://www.googleapis.com/auth/admin.reports.usage.readonly",
]

CUSTOMER_ID = os.getenv("GOOGLE_CUSTOMER_ID", "my_customer")

FIELDS = (
    "chromeosdevices(deviceId,serialNumber,model,status,osVersion,"
    "annotatedUser,lastEnrollmentTime,lastSync,recentUsers,"
    "lastKnownNetwork,orgUnitPath,annotatedLocation,macAddress,"
    "ethernetMacAddress,platformVersion,firmwareVersion)"
    ",nextPageToken"
)

# Seuils pour le matching
MAX_DEVICES_PER_USER = 5        # au-delà → flag "ambiguous"
OLD_PRINT_DAYS       = 60       # au-delà → WAN IP peu fiable
MAX_DELTA_HOURS      = 48       # fenêtre d'activité device vs impression

# ==============================================================
# MOTS-CLÉS POUR IDENTIFIER UNE IMPRIMANTE (USB)
# ==============================================================

# Mots-clés FORTS qui identifient une imprimante/scanner
SCANNER_KEYWORDS = ["canoscan", "lidescan", "lide ", "lide", "scanjet", "scansnap"]

PRINTER_STRONG_KEYWORDS = [
    "printer", "deskjet", "laserjet", "officejet", "envy", "pagewide",
    "pixma", "ecotank", "workforce", "imageclass", "mfc-", "dcp-", "hl-",
    "p-touch", "lq-", "l3110", "l3150", "l3250", "l3210", "l4260", "l5290",
    "lexmark", "xerox", "kyocera", "ricoh", "zebra", "dymo", "bixolon",
    "printer-80", "usb printer port",
]

# Mots-clés qui EXCLUENT d'office (faux positifs fréquents)
NON_PRINTER_KEYWORDS = [
    "mouse", "keyboard", "root hub", " hub", "camera", "webcam",
    "headset", "audio", "microphone", "mic ", "storage", "disk",
    "flash", "mtp", "android", "phone", "galaxy", "iphone",
    "touchpad", "gamepad", "joystick", "barcode", "reader",
    "ethernet", "wireless", "bluetooth", "receiver","motorola","moto g",
]

TELEMETRY_EVENT_TYPES = [
    "OS_CRASH",
    "USB_PERIPHERAL",
    "NETWORK_STATE_CHANGE",
    "HTTPS_LATENCY_CHANGE",
    "WIFI_SIGNAL_STRENGTH",
    "VPN_CONNECTION_STATE_CHANGE",
    "APP_INSTALL",
    "APP_UNINSTALL",
    "APP_LAUNCH",
    "EXTERNAL_DISPLAY",
    "AUDIO_SEVERE_UNDERRUN",
]

# Champs à récupérer (tous les champs spécifiques aux event types)
TELEMETRY_EVENTS_READ_MASK = (
    "name,device,user,reportTime,eventType,"
    "audioSevereUnderrunEvent,usbPeripheralsEvent,"
    "networkStateChangeEvent,httpsLatencyChangeEvent,"
    "wifiSignalStrengthEvent,vpnConnectionStateChangeEvent,"
    "appInstallEvent,appUninstallEvent,appLaunchEvent,"
    "externalDisplaysEvent,osCrashEvent"
)

# ==============================================================
# AUTHENTIFICATION
# ==============================================================

def get_credential():
    return get_credentials(TOKEN_FILE,SCOPES)

credentials = get_credential()
# ==============================================================
# RÉCUPÉRATION DES DEVICES
# ==============================================================
def get_devices(credentials):
    service = build("admin", "directory_v1", credentials=credentials,
                    cache_discovery=False)

    all_devices = []
    page_token = None

    while True:
        response = service.chromeosdevices().list(
            customerId=CUSTOMER_ID,
            maxResults=100,
            pageToken=page_token,
            projection="FULL",
            fields=FIELDS,
        ).execute()

        for device in response.get("chromeosdevices", []):
            device["lastSync"]           = format_date(device.get("lastSync"))
            device["lastEnrollmentTime"] = format_date(
                device.get("lastEnrollmentTime")
            )
            device["orgUnitPath"]        = format_org_unit(
                device.get("orgUnitPath")
            )
            all_devices.append(device)

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return all_devices


# ==============================================================
# TÉLÉMÉTRIE
# ==============================================================

def get_telemetry_devices(credentials):
    service = build("chromemanagement", "v1", credentials=credentials,
                    cache_discovery=False)
    all_devices = []
    page_token = None

    while True:
        response = service.customers().telemetry().devices().list(
            parent="customers/my_customer",
            readMask=(
                "name,customer,orgUnitId,deviceId,serialNumber,"
                "cpuInfo,cpuStatusReport,"
                "memoryInfo,memoryStatusReport,"
                "networkInfo,networkStatusReport,networkDiagnosticsReport,"
                "osUpdateStatus,"
                "graphicsInfo,graphicsStatusReport,"
                "batteryInfo,batteryStatusReport,"
                "storageInfo,storageStatusReport,"
                "thunderboltInfo,"
                "audioStatusReport,"
                "bootPerformanceReport,"
                "heartbeatStatusReport,"
                "kioskAppStatusReport,"
                "networkBandwidthReport,"
                "peripheralsReport,"
                "appReport,"
                "runtimeCountersReport"
            ),
            pageSize=100,
            pageToken=page_token,
        ).execute()

        batch = response.get("devices", [])
        all_devices.extend(batch)
        print(f"  → Page télémétrie : {len(batch)} devices "
              f"(total : {len(all_devices)})")

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return all_devices


def get_telemetry_events(credentials):
    service = build("chromemanagement", "v1", credentials=credentials,
                    cache_discovery=False)

    response = service.customers().telemetry().events().list(
        parent="customers/my_customer",
        filter="event_type=OS_CRASH",
        readMask=(
            "name,device,user,reportTime,eventType,"
            "audioSevereUnderrunEvent,usbPeripheralsEvent,"
            "networkStateChangeEvent,httpsLatencyChangeEvent,"
            "wifiSignalStrengthEvent,vpnConnectionStateChangeEvent,"
            "appInstallEvent,appUninstallEvent,appLaunchEvent,"
            "osCrashEvent,externalDisplaysEvent"
        ),
    ).execute()

    return response.get("events", [])


# ==============================================================
# AUDIT LOGS D'IMPRESSION
# ==============================================================

def get_print_audit_logs(credentials, days=90):
    """Événements d'impression Google Workspace (Docs, Sheets, Slides, Drive)."""
    service = build("admin", "reports_v1", credentials=credentials,
                    cache_discovery=False)

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
                    "ip":   item.get("ipAddress"),
                    "documentId": ev.get("parameters", [{}])[0].get("value")
                        if ev.get("parameters") else None,
                    "documentTitle": next(
                        (p["value"] for p in ev.get("parameters", [])
                         if p.get("name") == "doc_title"),
                        None,
                    ),
                })

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return all_events


PRINTER_CLASS = 7
def _text(usb):
    return f"{usb.get('vendor') or ''} {usb.get('name') or ''}".lower()

def is_printer_peripheral(usb, include_scanners=False):
    if not usb:
        return False

    name = (usb.get("name") or "").lower().strip()
    text = _text(usb)               # fabricant + nom
    if not name:
        return False

    # 1) Exclusions d'abord, sur fabricant + nom
    if any(kw in text for kw in NON_PRINTER_KEYWORDS):
        return False

    if not include_scanners and any(kw in name for kw in SCANNER_KEYWORDS):
        return False

    # 3) Signal fiable : classe USB Printer
    class_codes = usb.get("classCodes") or [usb.get("classId")]
    if PRINTER_CLASS in class_codes:
        return True

    # 4) Sinon mots-clés
    return any(kw in text for kw in PRINTER_STRONG_KEYWORDS)
    

def extract_printers_from_telemetry(telemetry_devices):
    """Extrait toutes les imprimantes USB vues dans la télémétrie."""
    printers = []

    for tel in telemetry_devices:
        device_id    = tel.get("deviceId", "?")
        serial       = tel.get("serialNumber", "?")
        org_unit_id  = tel.get("orgUnitId", "?")

        for report in tel.get("peripheralsReport", []) or []:
            report_time = report.get("reportTime")
            for usb in report.get("usbPeripheralReport", []) or []:
                if not is_printer_peripheral(usb):
                    continue
                printers.append({
                    "deviceId":           device_id,
                    "deviceSerialNumber": serial,
                    "orgUnitId":          org_unit_id,
                    "vendor":             usb.get("vendor", "Inconnu"),
                    "model":              usb.get("name",   "Inconnu"),
                    "vid":                usb.get("vid"),
                    "pid":                usb.get("pid"),
                    "connectionType":     "USB",
                    "lastSeen":           report_time,
                })

    # Déduplication : (deviceId, vid, pid, model) → garde le plus récent
    seen = {}
    for p in printers:
        key = (p["deviceId"], p["vid"], p["pid"], p["model"])
        existing = seen.get(key)
        if not existing or (p["lastSeen"] and
                            p["lastSeen"] > existing["lastSeen"]):
            seen[key] = p

    return list(seen.values())


def build_device_printers_index(detected_printers):
    """
    Index deviceId -> liste d'imprimantes USB vues sur ce device.
    Fusionne par (vid, pid, model) pour éviter les doublons.
    """
    index = defaultdict(dict)   # deviceId -> {(vid,pid,model): printer}

    for p in detected_printers:
        dev_id = p.get("deviceId")
        if not dev_id:
            continue
        key = (p.get("vid"), p.get("pid"), p.get("model"))
        existing = index[dev_id].get(key)
        if not existing or (p.get("lastSeen") and
                            p["lastSeen"] > existing.get("lastSeen", "")):
            index[dev_id][key] = p

    # Convertit en listes
    return {dev_id: list(printers.values())
            for dev_id, printers in index.items()}


# ==============================================================
# ★ MATCHING PAR EMAIL — avec gestion des 5 cas
# ==============================================================

def parse_dt(s):
    """Parse ISO8601 (avec/sans 'Z') ou format FR '02/10/2026 04:33:01'."""
    if not s:
        return None
    s = s.strip()

    # ISO8601
    try:
        if s.endswith("Z"):
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        pass

    # Format FR
    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    return None


def build_email_index(devices):
    """
    Construit l'index email -> liste de devices où l'utilisateur est apparu.
    Utilise `recentUsers` pour le mapping.
    """
    email_to_devices = defaultdict(list)

    for d in devices:
        device_meta = {
            "deviceId":     d.get("deviceId"),
            "serialNumber": d.get("serialNumber"),
            "model":        d.get("model"),
            "orgUnitPath":  d.get("orgUnitPath"),
            "lastSync":     d.get("lastSync"),
            "status":       d.get("status"),
            "ipAddress":    None,
            "wanIpAddress": None,
        }

        nets = d.get("lastKnownNetwork") or []
        if nets:
            device_meta["ipAddress"]    = nets[0].get("ipAddress")
            device_meta["wanIpAddress"] = nets[0].get("wanIpAddress")

        for u in d.get("recentUsers", []):
            email = (u.get("email") or "").lower().strip()
            if email:
                email_to_devices[email].append(device_meta)

    return email_to_devices


def extract_managed_domains(devices):
    """
    Extrait les domaines email managés depuis les devices.
    Sert à détecter les utilisateurs "unmanaged" (hors parc).
    """
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
    """
    Index deviceId -> { heartbeats: [dt], network_reports: [(dt, lanIP)] }
    Sert au départage temporel.
    """
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
            "heartbeats":      sorted(heartbeats),
            # ✅ Tri uniquement sur la 1ère clé (datetime)
            "network_reports": sorted(net_reports, key=lambda x: x[0]),
        }
    return idx


def match_print_to_devices(print_log, email_index, telemetry_index,
                           managed_domains,
                           max_delta_hours=MAX_DELTA_HOURS):
    """
    Retourne (candidats, flags).
    Cas gérés :
      1) USER_TYPE_UNMANAGED → flag unmanaged_user
      2) Email sur 0 device  → flag unmatched_user
      3) Email sur >5 device → flag ambiguous (au niveau appelant)
      4) Impression > 60 j   → bonus WAN IP réduit
      5) documentId null     → flag no_document_id
    """
    user = (print_log.get("user") or "").lower().strip()
    ip   = print_log.get("ip")
    t    = parse_dt(print_log.get("time"))
    now  = datetime.now(timezone.utc)

    flags = {
        "unmanaged_user":  False,
        "unmatched_user":  False,
        "no_document_id":  not print_log.get("documentId"),
    }

    # ─── Cas 1 : détection "unmanaged" par domaine ───
    domain = user.split("@", 1)[1] if "@" in user else ""
    if domain and domain not in managed_domains:
        flags["unmanaged_user"] = True

    # ─── Cas 2 : email présent sur 0 device ───
    matches = email_index.get(user, [])
    if not matches:
        flags["unmatched_user"] = True
        return [], flags

    # ─── Cas 4 : ancienneté de l'impression ───
    age_days = (now - t).days if t else 0
    old_print = age_days > OLD_PRINT_DAYS

    candidates = []

    for dev in matches:
        score  = 50                    # base : email trouvé
        reason = ["email OK"]

        # Bonus WAN IP (poids normal si récent, réduit si ancien)
        if ip and dev.get("wanIpAddress") == ip:
            if old_print:
                score += 5
                reason.append(
                    f"WAN IP OK (impression >{OLD_PRINT_DAYS}j, poids réduit)"
                )
            else:
                score += 30
                reason.append("WAN IP OK")

        # Bonus activité récente autour de l'impression
        if t and dev["deviceId"] in telemetry_index:
            tel = telemetry_index[dev["deviceId"]]

            hbs_before = [h for h in tel["heartbeats"] if h <= t]
            if hbs_before:
                delta_h = (t - max(hbs_before)).total_seconds() / 3600
                if delta_h <= max_delta_hours:
                    score += 20
                    reason.append(f"actif il y a {delta_h:.1f}h")

            # Bonus : LAN récent = IP du log
            for n_dt, n_ip in reversed(tel["network_reports"]):
                if n_dt <= t:
                    if n_ip and n_ip == ip:
                        score += 10
                        reason.append("LAN récent = IP log")
                    break

        candidates.append({
            "device": dev,
            "score":  score,
            "reason": " + ".join(reason),
        })

    candidates.sort(key=lambda c: c["score"], reverse=True)
    return candidates, flags


def enrich_print_logs(print_logs, devices, telemetry, detected_printers):
    """
    Enrichit chaque log d'impression avec :
      - le device matché (par email)
      - les imprimantes USB attachées à ce device
      - un flag 'likely_printer' si une seule imprimante détectée
    Produit aussi la liste des emails non trouvés.
    """
    email_index      = build_email_index(devices)
    telemetry_index  = build_telemetry_index(telemetry)
    managed_domains  = extract_managed_domains(devices)
    device_printers  = build_device_printers_index(detected_printers)

    enriched        = []
    unmatched_users = defaultdict(lambda: {
        "count": 0,
        "documents": [],
        "first_seen": None,
        "last_seen": None,
    })

    stats = {
        "total":               len(print_logs),
        "matched":             0,
        "matched_confident":   0,   # score >= 80
        "ambiguous":           0,
        "unmatched":           0,
        "no_device":           0,
        "unmanaged_users":     0,
        "no_document_id":      0,
        "old_prints":          0,
        # ★ Stats imprimantes
        "with_printer_single":   0,
        "with_printer_multiple": 0,
        "no_printer_on_device":  0,
    }

    for log in print_logs:
        cands, flags = match_print_to_devices(
            log, email_index, telemetry_index, managed_domains
        )

        best = cands[0] if cands and cands[0]["device"] else None

        device_candidates = [c for c in cands if c["device"]]
        many_devices = len(device_candidates) > MAX_DEVICES_PER_USER
        ambiguous    = (len(device_candidates) > 1) or many_devices

        # ─── Cas 2 : email sur 0 device ───
        if flags["unmatched_user"]:
            user = (log.get("user") or "").lower().strip()
            entry = unmatched_users[user]
            entry["count"] += 1
            entry["documents"].append({
                "time":          log.get("time"),
                "documentTitle": log.get("documentTitle"),
                "ip":            log.get("ip"),
            })
            t_str = log.get("time")
            if t_str:
                if entry["first_seen"] is None or t_str < entry["first_seen"]:
                    entry["first_seen"] = t_str
                if entry["last_seen"]  is None or t_str > entry["last_seen"]:
                    entry["last_seen"]  = t_str
            entry["unmanaged_user"] = flags["unmanaged_user"]

        # ★ Récupère les imprimantes du device matché
        attached_printers  = []
        likely_printer     = None
        printer_confidence = "none"

        if best and best["device"]:
            dev_id = best["device"]["deviceId"]
            attached_printers = device_printers.get(dev_id, [])

            if len(attached_printers) == 1:
                likely_printer     = attached_printers[0]
                printer_confidence = "single"
                stats["with_printer_single"] += 1
            elif len(attached_printers) > 1:
                printer_confidence = "multiple"
                stats["with_printer_multiple"] += 1
            else:
                stats["no_printer_on_device"] += 1

        # ─── Construction de l'entrée enrichie ───
        entry = {
            "user":          log.get("user"),
            "time":          log.get("time"),
            "ip":            log.get("ip"),
            "documentId":    log.get("documentId"),
            "documentTitle": log.get("documentTitle"),

            "matched_device": best["device"] if best else None,
            "match_score":    best["score"]  if best else 0,
            "match_reason":   best["reason"] if best else "non matché",

            # ★ Imprimantes du device
            "attached_printers":  attached_printers,
            "likely_printer":     likely_printer,
            "printer_confidence": printer_confidence,

            "flags": {
                "ambiguous":      ambiguous,
                "many_devices":   many_devices,
                "unmanaged_user": flags["unmanaged_user"],
                "unmatched_user": flags["unmatched_user"],
                "no_document_id": flags["no_document_id"],
            },

            "all_candidates": [
                {
                    "deviceId": c["device"]["deviceId"] if c["device"] else None,
                    "score":    c["score"],
                    "reason":   c["reason"],
                }
                for c in cands
            ],
        }
        enriched.append(entry)

        # ─── Stats ───
        if flags["no_document_id"]:
            stats["no_document_id"] += 1
        if flags["unmanaged_user"]:
            stats["unmanaged_users"] += 1
        if best and (t := parse_dt(log.get("time"))) and \
           (datetime.now(timezone.utc) - t).days > OLD_PRINT_DAYS:
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


# ==============================================================
# MAIN
# ==============================================================

if __name__ == "__main__":
    creds = get_credential()

    # --- 1) Devices ---
    print("--- Récupération des devices ---")
    devices = get_devices(creds)
    print(f"✅ {len(devices)} devices récupérés\n")

    # --- 2) Télémétrie ---
    print("--- Récupération de la télémétrie (périphériques USB) ---")
    telemetry_devices = get_telemetry_devices(creds)
    print(f"✅ {len(telemetry_devices)} télémetry devices récupérés\n")

    # --- 3) Audit logs d'impression ---
    print("--- Récupération des audit logs d'impression ---")
    audit_logs = get_print_audit_logs(creds, days=90)
    print(f"✅ {len(audit_logs)} impressions trouvées\n")

    # ==========================================================
    # IMPRIMANTES DÉTECTÉES
    # ==========================================================
    print("=" * 60)
    print("★ IMPRIMANTES DÉTECTÉES VIA TÉLÉMÉTRIE (USB)")
    print("=" * 60)
    printers = extract_printers_from_telemetry(telemetry_devices)
    print(f"Total : {len(printers)} imprimante(s) unique(s)\n")

    by_model = defaultdict(list)
    for p in printers:
        by_model[(p["vendor"], p["model"])].append(p)

    print("Regroupement par modèle :")
    for (vendor, model), items in sorted(by_model.items()):
        devices_count = len(set(i["deviceId"] for i in items))
        print(f"   • {vendor} — {model}  ({devices_count} device(s))")

    # ==========================================================
    # CROISEMENT IMPRESSIONS ↔ DEVICES (par email + imprimante)
    # ==========================================================
    print("\n" + "=" * 60)
    print("★ CROISEMENT : qui a imprimé, depuis quel device")
    print("=" * 60)

    # ★ On passe `printers` pour attacher les imprimantes
    enriched_logs, unmatched_users, stats = enrich_print_logs(
        audit_logs, devices, telemetry_devices, printers
    )

    print(f"   Total impressions          : {stats['total']}")
    print(f"   Rattachees (score≥80)    : {stats['matched_confident']}")
    print(f"   Rattachees (total)       : {stats['matched']}")
    print(f"   Ambigues                 : {stats['ambiguous']}")
    print(f"   Sans device              : {stats['no_device']}")
    print(f"   Non matchées             : {stats['unmatched']}")
    print(f"   Utilisateurs unmanaged  : {stats['unmanaged_users']}")
    print(f"   Sans documentId         : {stats['no_document_id']}")
    print(f"   Impressions > {OLD_PRINT_DAYS}j        : {stats['old_prints']}")
    print(f"   Device avec 1 impr.     : {stats['with_printer_single']}")
    print(f"   Device avec >1 impr.    : {stats['with_printer_multiple']}")
    print(f"   Device sans impr. connue: {stats['no_printer_on_device']}")

    # Aperçu des 5 premiers matchés
    matched_logs = [l for l in enriched_logs if l.get("matched_device")]
    if matched_logs:
        print("\nAperçu (5 premiers matchés) :")
        for log in matched_logs[:5]:
            dev = log["matched_device"]
            print(f"   [{log['time']}]  score={log['match_score']}")
            print(f"      User   : {log['user']}")
            print(f"      Doc    : {log['documentTitle']}")

            # ★ Affichage imprimante
            conf = log["printer_confidence"]
            if conf == "single":
                p = log["likely_printer"]
                print(f"      Imprimante : {p['vendor']} {p['model']}  ")
            elif conf == "multiple":
                names = ", ".join(
                    f"{p['vendor']} {p['model']}"
                    for p in log["attached_printers"]
                )
                print(f"      Imprimantes: {names}  ⚠ (ambigu)")
            else:
                print(f"      Imprimante : aucune USB détectée sur ce device")

            print(f"      Device : {dev['serialNumber']} ({dev['model']})")
            print(f"      OU     : {dev['orgUnitPath']}")
            print(f"      Raison : {log['match_reason']}")
            if log["flags"]["ambiguous"]:
                print(f"      ⚠ Ambigu ({len(log['all_candidates'])} candidats)")
            print("   " + "-" * 36)

    # Top utilisateurs non matchés
    if unmatched_users:
        print(f"\nTop 5 utilisateurs non trouvés dans les devices :")
        top_unmatched = sorted(
            unmatched_users.items(),
            key=lambda kv: kv[1]["count"],
            reverse=True,
        )[:5]
        for email, info in top_unmatched:
            tag = "unmanaged" if info.get("unmanaged_user") else "inconnu"
            print(f"   • {email:45s} {info['count']:5d} impressions  [{tag}]")

    # ==========================================================
    # SAUVEGARDES
    # ==========================================================
    # print("\n--- Sauvegarde des résultats ---")

    # if devices:
    #     save(devices, "devices", "Inventaire devices", formatter=str)
    #     save_to_json(devices, "devices")

    # if telemetry_devices:
    #     save(telemetry_devices, "telemetry_devices",
    #          "Télémétrie - Appareils", formatter=str)
    #     save_to_json(telemetry_devices, "telemetry_devices")

    # if audit_logs:
    #     save(audit_logs, "print_audit_logs",
    #          "Historique impressions", formatter=str)
    #     save_to_json(audit_logs, "print_audit_logs")

    # if printers:
    #     save(printers, "detected_printers",
    #          "Imprimantes détectées via USB", formatter=str)
    #     save_to_json(printers, "detected_printers")

    # if enriched_logs:
    #     save(enriched_logs, "enriched_print_logs",
    #          "Impressions croisées avec devices", formatter=str)
    #     save_to_json(enriched_logs, "enriched_print_logs")

    # if unmatched_users:
    #     save(unmatched_users, "unmatched_users",
    #          "Utilisateurs d'impression absents du parc de devices",
    #          formatter=str)
    #     save_to_json(unmatched_users, "unmatched_users")

    # ==========================================================
    # DIAGNOSTIC FINAL
    # ==========================================================
    print("\n--- Diagnostic ---")
    print(f"   Devices                     : {len(devices)}")
    print(f"   Télémétries (USB)           : {len(telemetry_devices)}")
    print(f"   Imprimantes USB détectées   : {len(printers)}")
    print(f"   Impressions (audit logs)    : {len(audit_logs)}")
    print(f"   Impressions rattachées      : {stats['matched']}")
    print(f"   Utilisateurs non trouvés    : {len(unmatched_users)}")