import argparse
import csv
import json
import os
from concurrent.futures import ThreadPoolExecutor
from bisect import bisect_right
from types import SimpleNamespace
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from backend.utils.get_credential import get_credentials 
from backend.utils.parser import as_list, parse_dur, parse_ts, safe_ts, flatten, paginate

def get_credential():
    return get_credentials(TOKEN_FILE, SCOPES)

CONTEXT_LOOKBACK = timedelta(hours=2)   # le "dernier utilisateur" regarde jusqu'à 24 h avant
def _z(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _event_filter(et, cutoff, use_ts=True):
    f = f"event_type={et}"
    if use_ts and cutoff:
        f += f' AND timestamp>="{cutoff}"'
    return f

BASE_DIR = Path(__file__).resolve().parents[3]
OUTPUT_DIR = BASE_DIR / "output"
HISTORY_FILE = OUTPUT_DIR / "history_event" / "crash_history.csv"
_token_env_path = os.getenv("GOOGLE_TOKEN_PATH", "credential/token.json")
_candidate_path = Path(_token_env_path) if Path(_token_env_path).is_absolute() else (BASE_DIR / _token_env_path).resolve()

if not _candidate_path.exists():
    _fallback = (BASE_DIR / "credential" / "token.json").resolve()
    TOKEN_FILE = _fallback if _fallback.exists() else _candidate_path
else:
    TOKEN_FILE = _candidate_path
OUTPUT_DIR = BASE_DIR / "output"

CUSTOMER_ID = "my_customer"

SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly",
    "https://www.googleapis.com/auth/chrome.management.telemetry.readonly",
]

credentials = get_credential()
# Crash rapporté <= N minutes après un démarrage : très probablement un crash de la SESSION
# PRÉCÉDENTE, remonté au reboot (le rapport est envoyé au boot suivant).
BOOT_REPORT_MIN = 15

# Événements "contexte" (ce que faisait la machine avant). Si un type n'existe pas / n'est pas
# activé dans la console Admin, il est simplement ignoré. Adaptez les noms de champs si besoin.
CONTEXT_EVENT_TYPES = [
    "USB_ADDED", "USB_REMOVED",
    "NETWORK_STATE_CHANGE",
    "VPN_CONNECTION_STATE_CHANGE", "AUDIO_SEVERE_UNDERRUN",
]

EVENT_PAYLOAD_FIELD = {
    "APP_LAUNCHED": "appLaunchEvent",
    "APP_INSTALLED": "appInstallEvent",
    "APP_UNINSTALLED": "appUninstallEvent",
    "USB_ADDED": "usbPeripheralsEvent",
    "USB_REMOVED": "usbPeripheralsEvent",
    "NETWORK_STATE_CHANGE": "networkStateChangeEvent",
    "NETWORK_HTTPS_LATENCY_CHANGE": "httpsLatencyChangeEvent",
    "VPN_CONNECTION_STATE_CHANGE": "vpnConnectionStateChangeEvent",
    "AUDIO_SEVERE_UNDERRUN": "audioSevereUnderrunEvent",
}

# Champs télémétrie appareil (testés un par un : ceux non dispo sont ignorés)
TELEMETRY_OPTIONAL_FIELDS = [
    "osUpdateStatus", "runtimeCountersReport", "cpuStatusReport", "memoryStatusReport",
    "storageStatusReport", "networkStatusReport", "heartbeatStatusReport",
]

STATUS_PREFIX = {
    "cpuStatusReport": "cpu", "memoryStatusReport": "mem", "storageStatusReport": "disk",
    "networkStatusReport": "net", "heartbeatStatusReport": "hb", "runtimeCountersReport": "rt",
}

_DIR_BASE = ("deviceId,serialNumber,model,status,osVersion,platformVersion,"
             "firmwareVersion,orgUnitPath,recentUsers(email),lastSync")
_DIR_EXTRA = ("bootMode,annotatedUser,annotatedLocation,annotatedAssetId,notes,lastEnrollmentTime,"
              "supportEndDate,autoUpdateExpiration,manufactureDate,systemRamTotal,"
              "lastKnownNetwork(ipAddress,wanIpAddress),recentUsers(email,type),"
              "activeTimeRanges(date,activeTime)")

def load_directory(creds):
    """Retourne (index deviceId->infos, activité deviceId->{date: minutes actives})."""
    svc = build("admin", "directory_v1", credentials=creds, cache_discovery=False)

    def run(fields):
        index, activity = {}, {}
        for d in paginate(svc.chromeosdevices().list, "chromeosdevices",
                          customerId=CUSTOMER_ID, maxResults=100,
                          projection="FULL",           # BASIC ne renvoie pas model/osVersion
                          fields=fields):
            recent = d.get("recentUsers") or []
            net = (d.get("lastKnownNetwork") or [{}])[0]
            index[d["deviceId"]] = {
                "deviceId": d["deviceId"],
                "serial": d.get("serialNumber"),
                "model": d.get("model"),
                "osVersion": d.get("osVersion"),
                "platformVersion": d.get("platformVersion"),
                "firmware": d.get("firmwareVersion"),
                "bootMode": d.get("bootMode"),
                "orgUnit": d.get("orgUnitPath"),
                "status": d.get("status"),
                "lastSync": d.get("lastSync"),
                "lastEnrollment": d.get("lastEnrollmentTime"),
                "supportEndDate": d.get("supportEndDate"),
                "autoUpdateExpiration": d.get("autoUpdateExpiration"),
                "manufactureDate": d.get("manufactureDate"),
                "ramTotal": d.get("systemRamTotal"),
                "lastIp": net.get("ipAddress"),
                "lastWanIp": net.get("wanIpAddress"),
                "annotatedUser": d.get("annotatedUser"),
                "annotatedLocation": d.get("annotatedLocation"),
                "annotatedAssetId": d.get("annotatedAssetId"),
                "notes": d.get("notes"),
                "lastUser": recent[0].get("email") if recent else None,   # approximatif
                "recentUsers": "; ".join(r.get("email", "") for r in recent[:3]) or None,
            }
            activity[d["deviceId"]] = {
                a["date"]: a.get("activeTime") for a in (d.get("activeTimeRanges") or []) if a.get("date")
            }
        return index, activity

    try:
        return run(f"chromeosdevices({_DIR_BASE},{_DIR_EXTRA}),nextPageToken")
    except HttpError as e:
        print(f"  ⚠️ Champs Directory étendus refusés ({e.resp.status}) -> champs de base seulement")
        return run(f"chromeosdevices({_DIR_BASE}),nextPageToken")


def device_info(directory, device_id):
    return directory.get(device_id) or {"deviceId": device_id}

# ------------------------------------------------------------------
# Telemetry : événements de crash
# ------------------------------------------------------------------
# def fetch_os_crash_events(creds, directory, cutoff):

#     svc = build("chromemanagement", "v1", credentials=creds, cache_discovery=False)
#     out, raw = [], []
#     for ev in paginate(
#         svc.customers().telemetry().events().list, "telemetryEvents",
#         parent=f"customers/{CUSTOMER_ID}",
#         filter="event_type=OS_CRASH",
#         readMask="name,device,user,reportTime,eventType,osCrashEvent",
#         pageSize=100,
#     ):
#         t = ev.get("reportTime", "")
#         if t < cutoff:
#             continue
#         raw.append(ev)
#         dev = ev.get("device") or {}
#         user = ev.get("user") or {}
#         crash = ev.get("osCrashEvent") or {}
#         out.append({
#             "time": t,
#             "eventName": ev.get("name"),
#             "crashType": crash.get("crashType") or "UNKNOWN",
#             "eventUserEmail": user.get("userEmail"),
#             "eventUserId": user.get("userId"),
#             "machine": dev.get("machine"),
#             # tout autre champ renvoyé par l'API dans osCrashEvent (sessionType, etc.)
#             **{f"crash.{k}": v for k, v in flatten(crash).items() if k != "crashType"},
#             **device_info(directory, dev.get("deviceId")),
#         })
#     return out, raw

def fetch_os_crash_events(creds, directory, cutoff):
    svc = build("chromemanagement", "v1", credentials=creds, cache_discovery=False)

    def lister(use_ts):
        return list(paginate(
            svc.customers().telemetry().events().list, "telemetryEvents",
            parent=f"customers/{CUSTOMER_ID}",
            filter=_event_filter("OS_CRASH", cutoff, use_ts),
            readMask="name,device,user,reportTime,eventType,osCrashEvent",
            pageSize=1000,
        ))

    try:
        evenements = lister(True)
    except HttpError as e:
        if e.resp.status != 400:
            raise
        print("  ⚠️ filtre timestamp refusé -> repli sans filtre de date")
        evenements = lister(False)

    out, raw = [], []
    for ev in evenements:
        t = ev.get("reportTime", "")
        if t < cutoff:
            continue
        raw.append(ev)
        dev = ev.get("device") or {}
        user = ev.get("user") or {}
        crash = ev.get("osCrashEvent") or {}
        out.append({
            "time": t,
            "eventName": ev.get("name"),
            "crashType": crash.get("crashType") or "UNKNOWN",
            "eventUserEmail": user.get("userEmail"),
            "eventUserId": user.get("userId"),
            "machine": dev.get("machine"),
            **{f"crash.{k}": v for k, v in flatten(crash).items() if k != "crashType"},
            **device_info(directory, dev.get("deviceId")),
        })
    return out, raw


# def _fetch_one_context_type(creds, et, cutoff):

#     svc = build("chromemanagement", "v1", credentials=creds, cache_discovery=False)  # 1 service par thread
#     payload_key = EVENT_PAYLOAD_FIELD.get(et)
#     mask = "name,device,user,reportTime,eventType" + (f",{payload_key}" if payload_key else "")
#     out, token, prev_max = [], None, None
#     try:
#         while True:
#             resp = svc.customers().telemetry().events().list(
#                 parent=f"customers/{CUSTOMER_ID}", filter=f"event_type={et}",
#                 readMask=mask, pageSize=1000, pageToken=token,        # 1000 au lieu de 100
#             ).execute()
#             evs = resp.get("telemetryEvents", [])
#             for ev in evs:
#                 t = ev.get("reportTime", "")
#                 dt = safe_ts(t)
#                 dev_id = (ev.get("device") or {}).get("deviceId")
#                 if t < cutoff or not dt or not dev_id:
#                     continue
#                 payload = ev.get(payload_key) if payload_key else None
#                 out.append({
#                     "deviceId": dev_id, "t": dt, "type": et,
#                     "user": (ev.get("user") or {}).get("userEmail"),
#                     "detail": json.dumps(payload, ensure_ascii=False, separators=(",", ":"))[:150] if payload else "",
#                 })
#             # arrêt anticipé : si l'API renvoie du plus récent au plus ancien et que toute
#             # la page est avant le cutoff, la suite sera encore plus ancienne
#             if evs:
#                 page_max = max(e.get("reportTime", "") for e in evs)
#                 if page_max < cutoff and prev_max is not None and page_max < prev_max:
#                     break
#                 prev_max = page_max
#             token = resp.get("nextPageToken")
#             if not token:
#                 break
#     except HttpError as e:
#         return et, [], f"ignoré (HTTP {e.resp.status})"
#     return et, out, None

def _fetch_one_context_type(creds, et, cutoff):
    svc = build("chromemanagement", "v1", credentials=creds, cache_discovery=False)
    payload_key = EVENT_PAYLOAD_FIELD.get(et)
    mask = "name,device,user,reportTime,eventType" + (f",{payload_key}" if payload_key else "")
    out, token, prev_max = [], None, None
    use_ts = True
    try:
        while True:
            try:
                resp = svc.customers().telemetry().events().list(
                    parent=f"customers/{CUSTOMER_ID}",
                    filter=_event_filter(et, cutoff, use_ts),
                    readMask=mask, pageSize=1000, pageToken=token,
                ).execute(num_retries=3)
            except HttpError as e:
                if use_ts and e.resp.status == 400:
                    use_ts = False                      # repli : filtre date refusé
                    out, token, prev_max = [], None, None
                    continue
                raise
            evs = resp.get("telemetryEvents", [])
            for ev in evs:
                t = ev.get("reportTime", "")
                dt = safe_ts(t)
                dev_id = (ev.get("device") or {}).get("deviceId")
                if t < cutoff or not dt or not dev_id:
                    continue
                payload = ev.get(payload_key) if payload_key else None
                out.append({
                    "deviceId": dev_id, "t": dt, "type": et,
                    "user": (ev.get("user") or {}).get("userEmail"),
                    "detail": json.dumps(payload, ensure_ascii=False, separators=(",", ":"))[:150] if payload else "",
                })
            # arrêt anticipé : si l'API renvoie du plus récent au plus ancien et que toute
            # la page est avant le cutoff, la suite sera encore plus ancienne
            if evs:
                page_max = max(e.get("reportTime", "") for e in evs)
                if page_max < cutoff and prev_max is not None and page_max < prev_max:
                    break
                prev_max = page_max
            token = resp.get("nextPageToken")
            if not token:
                break
    except HttpError as e:
        return et, [], f"ignoré (HTTP {e.resp.status})"
    return et, out, None

def fetch_context_events(creds, types, cutoff):
    """Types d'événements récupérés en parallèle -> deviceId -> [{t, type, user, detail}] triés."""
    ctx = defaultdict(list)
    with ThreadPoolExecutor(max_workers=min(5, max(1, len(types)))) as ex:
        for et, evs, err in ex.map(lambda t: _fetch_one_context_type(creds, t, cutoff), types):
            print(f"  {et:<32} {err or str(len(evs)) + ' événements'}")
            for e in evs:
                ctx[e.pop("deviceId")].append(e)
    for v in ctx.values():
        v.sort(key=lambda x: x["t"])
    return ctx


# ------------------------------------------------------------------
# Telemetry : appareils (boot/arrêt + états)
# ------------------------------------------------------------------
_TEL_FIELDS = None

def fetch_device_telemetry(creds):
    global _TEL_FIELDS
    svc = build("chromemanagement", "v1", credentials=creds, cache_discovery=False)
    api = svc.customers().telemetry().devices()
    parent = f"customers/{CUSTOMER_ID}"

    if _TEL_FIELDS is None:
        fields = ["bootPerformanceReport"]
        for f in TELEMETRY_OPTIONAL_FIELDS:
            try:
                api.list(parent=parent, readMask=f"name,deviceId,{f}", pageSize=1).execute(num_retries=3)
                fields.append(f)
            except HttpError as e:
                if e.resp.status not in (400, 403, 404):
                    raise
                print(f"  champ télémétrie indisponible : {f} (HTTP {e.resp.status})")
        _TEL_FIELDS = fields
    fields = _TEL_FIELDS

    mask = "name,deviceId,serialNumber,orgUnitId," + ",".join(fields)
    return {
        t["deviceId"]: t
        for t in paginate(api.list, "devices", parent=parent, readMask=mask, pageSize=100)
        if t.get("deviceId")
    }

def build_boot_index(tel_by_dev):
    """deviceId -> (liste triée des heures de boot, lignes)."""
    idx = {}
    for dev, tel in tel_by_dev.items():
        rows = []
        for r in as_list(tel.get("bootPerformanceReport")):
            bt = safe_ts(r.get("bootUpTime") or r.get("reportTime"))
            if not bt:
                continue
            rows.append({
                "boot": bt,
                "shutdown": safe_ts(r.get("shutdownTime")),
                "reason": r.get("shutdownReason"),
                "boot_dur": parse_dur(r.get("bootUpDuration")),
                "shut_dur": parse_dur(r.get("shutdownDuration")),
            })
        rows.sort(key=lambda x: x["boot"])
        idx[dev] = ([r["boot"] for r in rows], rows)
    return idx


def build_status_index(tel_by_dev):
    """deviceId -> {champ: (heures triées, rapports)}"""
    idx = {}
    for dev, tel in tel_by_dev.items():
        per = {}
        for field in STATUS_PREFIX:
            pairs = []
            for r in as_list(tel.get(field)):
                dt = safe_ts(r.get("reportTime")) if isinstance(r, dict) else None
                if dt:
                    pairs.append((dt, r))
            pairs.sort(key=lambda p: p[0])
            if pairs:
                per[field] = ([p[0] for p in pairs], [p[1] for p in pairs])
        idx[dev] = per
    return idx


def boot_report_rows(tel_by_dev, directory, cutoff):
    out = []
    for dev, tel in tel_by_dev.items():
        for rep in as_list(tel.get("bootPerformanceReport")):
            t = rep.get("shutdownTime") or rep.get("reportTime") or ""
            if t < cutoff:
                continue
            out.append({
                "time": t,
                "bootUpTime": rep.get("bootUpTime"),
                "shutdownTime": rep.get("shutdownTime"),
                "shutdownReason": rep.get("shutdownReason"),
                "bootUpDuration": rep.get("bootUpDuration"),
                "shutdownDuration": rep.get("shutdownDuration"),
                **device_info(directory, dev),
            })
    return out


def build_context_index(ctx):
    return {dev: ([e["t"] for e in evs], evs) for dev, evs in ctx.items()}


# ------------------------------------------------------------------
# Incidents (dédoublonnage + rang par appareil)
# ------------------------------------------------------------------
def cluster_incidents(events, window_s=300):
    """Fusionne les événements du même appareil + même type espacés de <= window_s secondes."""
    by = defaultdict(list)
    for e in events:
        by[(e.get("deviceId"), e["crashType"])].append(e)
    incidents = []
    for evs in by.values():
        evs.sort(key=lambda e: parse_ts(e["time"]))
        cur = None
        for e in evs:
            t = parse_ts(e["time"])
            if cur is not None and (t - cur["_last"]).total_seconds() <= window_s:
                cur["raw_events"] += 1
                cur["_last"] = t
                if not cur.get("eventUserEmail") and e.get("eventUserEmail"):
                    cur["eventUserEmail"] = e["eventUserEmail"]
                    cur["eventUserId"] = e.get("eventUserId")
            else:
                cur = {**e, "raw_events": 1, "_last": t}
                incidents.append(cur)
    for i in incidents:
        i["last_event_time"] = i.pop("_last").isoformat()
        i["incident_key"] = f"{i.get('deviceId')}|{i['crashType']}|{i['time']}"
    incidents.sort(key=lambda i: parse_ts(i["time"]), reverse=True)
    return incidents


def add_sequence(incidents):
    """Rang du crash pour l'appareil + délai depuis le crash précédent (détection de boucles)."""
    by = defaultdict(list)
    for i in incidents:
        by[i.get("deviceId")].append(i)
    for evs in by.values():
        evs.sort(key=lambda i: parse_ts(i["time"]))
        prev = None
        for n, i in enumerate(evs, 1):
            t = parse_ts(i["time"])
            i["crash_seq"] = n
            i["minutes_since_prev_crash"] = round((t - prev).total_seconds() / 60, 1) if prev else None
            prev = t


# ------------------------------------------------------------------
# Enrichissement : cycle de vie, activité avant crash, état, indice de cause
# ------------------------------------------------------------------
def classify(inc, f):
    """Retourne (cause_class, cause_hint). Déduction par corrélation, PAS une cause prouvée."""
    reason, m = f.get("prev_shutdown_reason"), f.get("minutes_since_boot")
    parts = []
    if m is None:
        cls = "INDETERMINE"
        parts.append("aucun rapport de démarrage correspondant")
    else:
        at_boot = m <= BOOT_REPORT_MIN
        if reason == "SYSTEM_UPDATE":
            cls = "APRES_MISE_A_JOUR"
            parts.append("redémarrage consécutif à une mise à jour système")
        elif reason == "OTHER":
            cls = "ARRET_ANORMAL"
            parts.append("arrêt précédent non standard (coupure courant / extinction forcée / plantage)")
        elif at_boot:
            cls = "RAPPORT_AU_DEMARRAGE"
            parts.append("arrêt précédent normal mais crash remonté juste après le boot")
        else:
            cls = "EN_SESSION"
            parts.append("crash remonté en cours de session (>%d min après le boot)" % BOOT_REPORT_MIN)
        if at_boot:
            parts.append("probablement survenu dans la session précédente (rapport envoyé au reboot)")
        gap = f.get("offline_gap_min")
        if gap is not None and gap > 600:
            parts.append(f"machine restée éteinte {gap / 60:.0f} h avant ce boot")
    if inc["crashType"] == "CRASH_TYPE_EMBEDDED_CONTROLLER":
        parts.append("type EC : contrôleur embarqué (alim/thermique/firmware EC)")
    elif inc["crashType"] == "CRASH_TYPE_KERNEL":
        parts.append("type KERNEL : panic noyau (driver/matériel/mémoire)")
    mp = inc.get("minutes_since_prev_crash")
    if mp is not None and mp < 60:
        parts.append(f"crash répété ({mp:.0f} min après le précédent)")
    return cls, " | ".join(parts)


def _nearest_before(times_reps, T, max_age_min):
    if not times_reps:
        return None, None
    times, reps = times_reps
    i = bisect_right(times, T) - 1
    if i < 0 or (T - times[i]) > timedelta(minutes=max_age_min):
        return None, None
    return reps[i], round((T - times[i]).total_seconds() / 60, 1)


def enrich(inc, boots, ctx, status, tel_by_dev, activity, args):
    T = parse_ts(inc["time"])
    dev = inc.get("deviceId")
    f = {}

    # 1) cycle démarrage / arrêt
    times, rows = boots.get(dev, ([], []))
    i = bisect_right(times, T) - 1
    if i >= 0:
        r = rows[i]
        f["boot_time"] = r["boot"].isoformat()
        f["minutes_since_boot"] = round((T - r["boot"]).total_seconds() / 60, 1)
        f["boot_duration_s"] = r["boot_dur"]
        f["prev_shutdown_time"] = r["shutdown"].isoformat() if r["shutdown"] else None
        f["prev_shutdown_reason"] = r["reason"]
        f["prev_shutdown_duration_s"] = r["shut_dur"]
        f["offline_gap_min"] = (round((r["boot"] - r["shutdown"]).total_seconds() / 60, 1)
                                if r["shutdown"] else None)
    if i + 1 < len(rows):
        nb = rows[i + 1]["boot"]
        f["next_boot_time"] = nb.isoformat()
        f["minutes_to_next_boot"] = round((nb - T).total_seconds() / 60, 1)

    # 2) activité juste avant le crash
    last_user, last_user_src = None, None
    ctimes, cevs = ctx.get(dev, ([], []))
    if ctimes:
        j = bisect_right(ctimes, T)
        before = [e for e in cevs[:j] if (T - e["t"]) <= timedelta(minutes=args.context_minutes)]
        if before:
            last = before[-1]
            f["last_activity_time"] = last["t"].isoformat()
            f["last_activity_type"] = last["type"]
            f["last_activity_detail"] = last["detail"]
            f["seconds_since_last_activity"] = int((T - last["t"]).total_seconds())
            f["activities_before_crash"] = " || ".join(
                f"{(e['t'] + timedelta(hours=args.tz)).strftime('%H:%M:%S')} {e['type']} {e['detail']}".strip()
                for e in before[-args.context_count:]
            )
            f["activity_count_window"] = len(before)
        # dernier utilisateur vu dans les événements (24 h avant)
        for e in reversed(cevs[:j]):
            if (T - e["t"]) > timedelta(hours=24):
                break
            if e["user"]:
                last_user, last_user_src = e["user"], "activité<24h"
                break

    # 3) état de l'appareil juste avant (CPU, RAM, disque, réseau, heartbeat, runtime)
    for field, prefix in STATUS_PREFIX.items():
        rep, age = _nearest_before(status.get(dev, {}).get(field), T, args.report_max_age)
        if rep is not None:
            f[f"{prefix}.age_min"] = age
            for k, v in flatten({k: v for k, v in rep.items() if k != "reportTime"}).items():
                f[f"{prefix}.{k}"] = v
            if field == "runtimeCountersReport":
                up = parse_dur(rep.get("uptimeRuntimeDuration"))
                if up is not None:
                    f["uptime_runtime_h"] = round(up / 3600, 2)
    # snapshot actuel (au moment de la collecte, pas au moment du crash)
    for k, v in flatten((tel_by_dev.get(dev) or {}).get("osUpdateStatus") or {}).items():
        f[f"snapshot_os_update.{k}"] = v

    # 4) temps d'activité (Directory, minutes/jour)
    act = activity.get(dev) or {}
    if act:
        day = (T + timedelta(hours=args.tz)).strftime("%Y-%m-%d")
        prev_day = (T + timedelta(hours=args.tz) - timedelta(days=1)).strftime("%Y-%m-%d")
        f["active_min_crash_day"] = act.get(day)
        f["active_min_prev_day"] = act.get(prev_day)
        past = sorted(d for d in act if d <= day)
        f["last_active_date"] = past[-1] if past else None

    # 5) utilisateur (meilleure estimation)
    if inc.get("eventUserEmail"):
        f["lastUserBestGuess"], f["lastUserSource"] = inc["eventUserEmail"], "événement crash"
    elif last_user:
        f["lastUserBestGuess"], f["lastUserSource"] = last_user, last_user_src
    elif inc.get("lastUser"):
        f["lastUserBestGuess"], f["lastUserSource"] = inc["lastUser"], "Directory (approximatif)"

    # 6) indice de cause
    f["cause_class"], f["cause_hint"] = classify({**inc, **f}, f)
    inc.update(f)


# ------------------------------------------------------------------
# Résumés
# ------------------------------------------------------------------
def rate_table(title, incidents, fleet, key):
    fleet_n = Counter(key(d) for d in fleet)
    inc_n = Counter(key(i) for i in incidents)
    dev_n = defaultdict(set)
    for i in incidents:
        dev_n[key(i)].add(i.get("deviceId"))
    print(f"\n{title}")
    for k, n in sorted(inc_n.items(), key=lambda x: -x[1]):
        f, d = fleet_n.get(k, 0), len(dev_n[k])
        pct = f"{100 * d / f:.0f}%" if f else "?"
        per = f"{n / f:.1f}" if f else "?"
        print(f"  {str(k):<30} incidents={n:>5}   appareils touchés={d:>3}/{f:<3} ({pct:>4})   moy. par PC du parc={per}")


def summarize(raw_count, incidents, fleet, tz_offset):
    print(f"\n=== {raw_count} événements bruts -> {len(incidents)} incidents distincts ===")
    print("\nPar type :")
    counts = Counter()
    for i in incidents:
        t = i["crashType"]
        if t == "UNKNOWN":
            details = [f"{k.replace('crash.', '')}={v}" for k, v in i.items() if k.startswith("crash.") and v]
            if details:
                t = f"UNKNOWN ({', '.join(details)})"
        counts[t] += 1
    for k, n in counts.most_common():
        print(f"  {n:>5}  {k}")

    rate_table("Par version ChromeOS :", incidents, fleet, lambda x: x.get("osVersion"))
    rate_table("Par modèle :", incidents, fleet, lambda x: x.get("model"))
    rate_table("Par version firmware :", incidents, fleet, lambda x: x.get("firmware"))
    rate_table("Par filiale (OU) :", incidents, fleet, lambda x: x.get("orgUnit"))

    print("\nPar jour :")
    day_counts = Counter(parse_ts(i["time"]).strftime("%Y-%m-%d %a") for i in incidents)
    max_day = max(day_counts.values()) if day_counts else 1
    for k, n in sorted(day_counts.items()):
        bars = int(50 * n / max_day)
        print(f"  {k}  {n:>5}  {'#' * bars}")

    print(f"\nPar heure locale (UTC{tz_offset:+d}) :")
    h = Counter((parse_ts(i["time"]) + timedelta(hours=tz_offset)).hour for i in incidents)
    max_h = max(h.values()) if h else 1
    for hr in range(24):
        n = h.get(hr, 0)
        bars = int(50 * n / max_h)
        print(f"  {hr:02d}h  {n:>5}  {'#' * bars}")

    summarize_causes(incidents)

    ser = {i.get("deviceId"): i.get("serial") for i in incidents}
    usr = {i.get("deviceId"): i.get("lastUserBestGuess") for i in incidents}
    dev_causes = defaultdict(list)
    for i in incidents:
        dev_causes[i.get("deviceId")].append(i.get("crashType"))
    
    ou_devs = defaultdict(lambda: Counter())
    for i in incidents:
        ou = i.get("orgUnit") or "?"
        ou_devs[ou][i.get("deviceId")] += 1

    print("\nTous les appareils touchés (par filiale) :")
    for ou, devs in sorted(ou_devs.items()):
        print(f"  {ou} :")
        for dev, n in devs.most_common():
            top_cause = Counter(dev_causes[dev]).most_common(1)[0][0] if dev_causes[dev] else "N/A"
            print(f"    {n:>4}  {ser.get(dev)}  ({dev})  dernier user: {usr.get(dev)} | cause princ: {top_cause}")


def summarize_causes(incidents):
    print("\nRaison du dernier arrêt avant le crash :")
    for k, n in Counter(i.get("prev_shutdown_reason") for i in incidents).most_common():
        print(f"  {n:>5}  {k}")

    print("\nDélai entre le dernier boot et le crash :")
    buckets = Counter()
    for i in incidents:
        m = i.get("minutes_since_boot")
        if m is None:
            buckets["inconnu"] += 1
        elif m <= 2:
            buckets["0-2 min"] += 1
        elif m <= BOOT_REPORT_MIN:
            buckets[f"2-{BOOT_REPORT_MIN} min"] += 1
        elif m <= 60:
            buckets[f"{BOOT_REPORT_MIN}-60 min"] += 1
        elif m <= 240:
            buckets["1-4 h"] += 1
        else:
            buckets[">4 h"] += 1
    for k in ["0-2 min", f"2-{BOOT_REPORT_MIN} min", f"{BOOT_REPORT_MIN}-60 min", "1-4 h", ">4 h", "inconnu"]:
        if buckets.get(k):
            print(f"  {buckets[k]:>5}  {k}")

    loops = [i for i in incidents if (i.get("minutes_since_prev_crash") or 1e9) < 60]
    print(f"\nCrashs répétés (<1h après le précédent sur le même appareil) : {len(loops)}")
    print("Activité avant crash disponible pour "
          f"{sum(1 for i in incidents if i.get('last_activity_type'))}/{len(incidents)} incidents")


def device_summary(incidents, directory, tz):
    by = defaultdict(list)
    for i in incidents:
        by[i.get("deviceId")].append(i)
    rows = []
    for dev in dict.fromkeys(list(directory) + list(by)):
        info = device_info(directory, dev)
        evs = sorted(by.get(dev, []), key=lambda i: parse_ts(i["time"]))
        row = {k: info.get(k) for k in (
            "deviceId", "serial", "model", "orgUnit", "osVersion", "firmware", "bootMode", "status",
            "lastSync", "lastUser", "recentUsers", "lastWanIp", "annotatedUser", "annotatedLocation",
            "annotatedAssetId", "autoUpdateExpiration")}
        row.update({
            "crash_incidents": len(evs),
            "raw_events": sum(e["raw_events"] for e in evs),
            "kernel": sum(1 for e in evs if e["crashType"] == "CRASH_TYPE_KERNEL"),
            "embedded_controller": sum(1 for e in evs if e["crashType"] == "CRASH_TYPE_EMBEDDED_CONTROLLER"),
            "first_crash": evs[0]["time"] if evs else None,
            "last_crash": evs[-1]["time"] if evs else None,
            "days_with_crash": len({(parse_ts(e["time"]) + timedelta(hours=tz)).date() for e in evs}),
            "repeat_crashes_lt1h": sum(1 for e in evs if (e.get("minutes_since_prev_crash") or 1e9) < 60),
            "last_crash_user": next((e.get("lastUserBestGuess") for e in reversed(evs)
                                     if e.get("lastUserBestGuess")), None),
            "top_cause_class": (Counter(e.get("cause_class") for e in evs).most_common(1)[0][0]
                                if evs else None),
        })
        rows.append(row)
    rows.sort(key=lambda r: -r["crash_incidents"])
    return rows


SHORT_GAP_MIN = 3      # arrêt -> boot <= 3 min : reset / extinction forcée
MEDIUM_GAP_MIN = 60    # <= 1 h : coupure brève ; au-delà : coupure longue / batterie vide


def classify_other(boot, shutdown, crashes, crash_start):
    """Cause déduite d'un arrêt 'OTHER'. Retourne (classe, explication, crash_data_covered)."""
    covered = crash_start is not None and boot is not None and boot >= crash_start
    if boot is not None:
        for t, ctype in crashes:
            if boot - timedelta(minutes=1) <= t <= boot + timedelta(minutes=BOOT_REPORT_MIN):
                short = "KERNEL" if "KERNEL" in ctype else "EC" if "EMBEDDED" in ctype else ctype
                return (f"CRASH_{short}", f"crash {ctype} remonté juste après le reboot", True)
    if boot is None or shutdown is None:
        return "INCONNU", "heure d'arrêt ou de boot manquante", covered
    gap = (boot - shutdown).total_seconds() / 60
    note = "" if covered else " (pas de données crash sur cette période)"
    if gap <= SHORT_GAP_MIN:
        return "REDEMARRAGE_BRUSQUE", f"rallumé après {gap:.1f} min : reset / extinction forcée / plantage non rapporté{note}", covered
    if gap <= MEDIUM_GAP_MIN:
        return "ARRET_COURT", f"éteint {gap:.0f} min : coupure brève ou extinction forcée{note}", covered
    return "COUPURE_LONGUE", f"éteint {gap / 60:.1f} h : coupure de courant / batterie vide / débranché{note}", covered


def shutdown_events(boots, incidents, tz):
    crashes = defaultdict(list)
    for i in incidents:
        crashes[i.get("deviceId")].append((parse_ts(i["time"]), i["crashType"]))
    crash_start = min((t for v in crashes.values() for t, _ in v), default=None)
    rows = []
    for b in boots:
        reason = b.get("shutdownReason") or "INCONNU"
        boot, sd = safe_ts(b.get("bootUpTime")), safe_ts(b.get("shutdownTime"))
        row = {
            "orgUnit": b.get("orgUnit"), "serial": b.get("serial"), "model": b.get("model"),
            "shutdownReason": reason,
            "shutdownTime_local": (sd + timedelta(hours=tz)).strftime("%Y-%m-%d %H:%M:%S") if sd else None,
            "bootUpTime_local": (boot + timedelta(hours=tz)).strftime("%Y-%m-%d %H:%M:%S") if boot else None,
            "offline_min": round((boot - sd).total_seconds() / 60, 1) if boot and sd else None,
            "osVersion": b.get("osVersion"), "firmware": b.get("firmware"),
            "lastUser": b.get("lastUser"), "deviceId": b.get("deviceId"),
            "other_cause": None, "other_cause_hint": None, "crash_data_covered": None,
        }
        if reason == "OTHER":
            cls, hint, cov = classify_other(boot, sd, sorted(crashes.get(b.get("deviceId"), [])), crash_start)
            row.update(other_cause=cls, other_cause_hint=hint, crash_data_covered=cov)
        rows.append(row)
    rows.sort(key=lambda r: (r["orgUnit"] or "", r["shutdownReason"], r["shutdownTime_local"] or ""))
    return rows

def shutdown_by_device(rows):
    """Une ligne par PC : combien d'arrêts de chaque raison, et répartition des causes OTHER."""
    by = defaultdict(list)
    for r in rows:
        by[r["deviceId"]].append(r)
    out = []
    for dev, evs in by.items():
        c = Counter(e["shutdownReason"] for e in evs)
        oc = Counter(e["other_cause"] for e in evs if e["shutdownReason"] == "OTHER")
        out.append({
            "orgUnit": evs[0]["orgUnit"], "serial": evs[0]["serial"], "model": evs[0]["model"],
            "lastUser": evs[0]["lastUser"], "deviceId": dev,
            "USER_REQUEST": c.get("USER_REQUEST", 0),
            "OTHER": c.get("OTHER", 0),
            "SYSTEM_UPDATE": c.get("SYSTEM_UPDATE", 0),
            "OTHER_causes": ", ".join(f"{k}={n}" for k, n in oc.most_common()) or None,
        })
    out.sort(key=lambda r: (r["orgUnit"] or "", -r["OTHER"], -r["SYSTEM_UPDATE"]))
    return out


def summarize_shutdowns(rows, top=5):
    reasons = ["USER_REQUEST", "OTHER", "SYSTEM_UPDATE"]
    ous = sorted({r["orgUnit"] or "?" for r in rows})
    print("\nArrêts par filiale (événements / PC distincts) :")
    print(f"  {'filiale':<28}" + "".join(f"{r:>22}" for r in reasons))
    for ou in ous:
        line = f"  {ou:<28}"
        for reason in reasons:
            sel = [r for r in rows if (r["orgUnit"] or "?") == ou and r["shutdownReason"] == reason]
            line += f"{len(sel):>7} évts ({len({r['deviceId'] for r in sel}):>2} PC) "
        print(line)

    print("\nCause déduite des arrêts OTHER (par filiale) avec les PC les plus concernés :")
    for ou in ous:
        oc = Counter(r["other_cause"] for r in rows
                     if (r["orgUnit"] or "?") == ou and r["shutdownReason"] == "OTHER")
        if oc:
            parts = []
            for k, n in oc.most_common():
                pc_cnt = Counter(r["serial"] for r in rows
                                 if (r["orgUnit"] or "?") == ou and r["shutdownReason"] == "OTHER" and r["other_cause"] == k)
                top_pcs = ", ".join(f"{s}({c})" for s, c in pc_cnt.most_common(top))
                parts.append(f"{k}={n} [{top_pcs}]")
            print(f"  {ou:<28}\n      " + "\n      ".join(parts))

    for reason in ["SYSTEM_UPDATE"]:
        print(f"\nPC les plus concernés par {reason} :")
        for ou in ous:
            cnt = Counter(r["serial"] for r in rows
                          if (r["orgUnit"] or "?") == ou and r["shutdownReason"] == reason)
            if cnt:
                print(f"  {ou}: " + ", ".join(f"{s}({n})" for s, n in cnt.most_common(top)))
# ------------------------------------------------------------------
# Sauvegarde
# ------------------------------------------------------------------
# def save_rows(rows, name, ts):
#     OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
#     jp, cp = OUTPUT_DIR / f"{name}_{ts}.json", OUTPUT_DIR / f"{name}_{ts}.csv"
#     jp.write_text(json.dumps(rows, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
#     if rows:
#         cols = list(dict.fromkeys(k for r in rows for k in r))
#         with open(cp, "w", newline="", encoding="utf-8-sig") as f:   # utf-8-sig : accents OK dans Excel
#             w = csv.DictWriter(f, fieldnames=cols)
#             w.writeheader()
#             w.writerows(rows)
#     print(f"  {cp}")

def merge_history(rows, path=HISTORY_FILE):
    """Cumule les incidents dans un fichier unique (clé = incident_key). Garde l'existant."""
    path.parent.mkdir(parents=True, exist_ok=True)
    hist = {}
    if path.exists():
        with open(path, newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                hist[r["incident_key"]] = r
    new = 0
    for r in rows:
        if r["incident_key"] not in hist:
            hist[r["incident_key"]] = {k: ("" if v is None else v) for k, v in r.items()}
            new += 1
    allrows = sorted(hist.values(), key=lambda r: r.get("time", ""), reverse=True)
    cols = list(dict.fromkeys(k for r in allrows for k in r))
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, restval="")
        w.writeheader()
        w.writerows(allrows)
    print(f"  {path}  (+{new} nouveaux, {len(allrows)} au total)")

# ------------------------------------------------------------------
def main(credentials):
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--window", type=int, default=300, help="fenêtre de fusion des doublons (s)")
    ap.add_argument("--tz", type=int, default=3, help="décalage horaire local (Madagascar = 3)")
    ap.add_argument("--search", help="filtre texte sur toutes les colonnes")
    ap.add_argument("--no-context", action="store_true", help="ne pas récupérer les événements d'activité")
    ap.add_argument("--context-types", default=",".join(CONTEXT_EVENT_TYPES),
                    help="types d'événements d'activité, séparés par des virgules")
    ap.add_argument("--context-minutes", type=int, default=60, help="fenêtre d'activité avant crash (min)")
    ap.add_argument("--context-count", type=int, default=5, help="nb d'activités listées avant crash")
    ap.add_argument("--report-max-age", type=int, default=180,
                    help="âge max (min) d'un rapport d'état (CPU/RAM/...) pour être associé à un crash")
    ap.add_argument("--no-history", action="store_true", help="ne pas cumuler dans history/crash_history.csv")
    args = ap.parse_args()

    cutoff = (datetime.now(timezone.utc) - timedelta(days=args.days)).strftime("%Y-%m-%dT%H:%M:%SZ")

    print("Chargement Directory...")
    directory, activity = load_directory(credentials)
    print(f"  {len(directory)} appareils")

    print("Telemetry events (OS_CRASH)...")
    events, raw_events = fetch_os_crash_events(credentials, directory, cutoff)
    print(f"  {len(events)} événements bruts")
    if events:
        first = min(e["time"] for e in events)
        print(f"  Plus ancien événement : {first}  (fenêtre demandée : depuis {cutoff})")
        if parse_ts(first) - parse_ts(cutoff) > timedelta(days=2):
            print("  ⚠️ Les données commencent bien après le début de la fenêtre : la collecte a démarré à cette "
                  "date ou la rétention de l'API est limitée. Ne compare pas avec une période antérieure. "
                  "-> Lancez ce script chaque jour : history/crash_history.csv cumule les incidents.")

    print("Telemetry devices (boot/arrêt + états)...")
    tel_by_dev = fetch_device_telemetry(credentials)
    boots = boot_report_rows(tel_by_dev, directory, cutoff)
    print(f"  {len(boots)} rapports de démarrage/arrêt")
    print("  Raisons d'arrêt : " + ", ".join(f"{k}={n}" for k, n in Counter(b["shutdownReason"] for b in boots).most_common()))

    ctx = {}
    if not args.no_context:
        print("Telemetry events (activité avant crash)...")
        ctx = fetch_context_events(credentials, [t for t in args.context_types.split(",") if t], cutoff)

    incidents = cluster_incidents(events, args.window)
    add_sequence(incidents)

    boot_idx, status_idx, ctx_idx = build_boot_index(tel_by_dev), build_status_index(tel_by_dev), build_context_index(ctx)
    for inc in incidents:
        enrich(inc, boot_idx, ctx_idx, status_idx, tel_by_dev, activity, args)
    
    sd_rows = shutdown_events(boots, incidents, args.tz)
    summarize_shutdowns(sd_rows)

    if args.search:
        s = args.search.lower()
        incidents = [r for r in incidents if any(s in str(v).lower() for v in r.values())]
        print(f"\nFiltre '{args.search}' : {len(incidents)} incidents")

    summarize(len(events), incidents, list(directory.values()), args.tz)

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print("\nFichiers sauvegardés :")
    # save_rows(incidents, "chromeos_crash_incidents", ts)
    # save_rows(device_summary(incidents, directory, args.tz), "chromeos_device_summary", ts)
    # save_rows(boots, "chromeos_boot_reports", ts)
    # save_rows(sd_rows, "chromeos_shutdown_events", ts)              
    # save_rows(shutdown_by_device(sd_rows), "chromeos_shutdown_by_device", ts)  
    # (OUTPUT_DIR / f"chromeos_raw_events_{ts}.json").write_text(
    #     json.dumps(raw_events, indent=1, ensure_ascii=False), encoding="utf-8")
    # print(f"  {OUTPUT_DIR / f'chromeos_raw_events_{ts}.json'}")
    # if not args.no_history and not args.search:
    #     merge_history(incidents)
        
# def _directory_puis_crashs(creds, cutoff):
#     directory, activity = load_directory(creds)
#     events, _raw = fetch_os_crash_events(creds, directory, cutoff)
#     return directory, activity, events


# def get_crash_incidents(creds=None, debut=None, fin=None, days=90, window=300, tz=3,
#                         context_minutes=60, context_count=5,
#                         report_max_age=180, with_context=True):
#     # `fin` n'est pas utilisée : lire un peu plus récent est sans risque (doublons ignorés)
#     args = SimpleNamespace(
#         days=days, window=window, tz=tz, context_minutes=context_minutes,
#         context_count=context_count, report_max_age=report_max_age,
#     )
#     if debut is None:
#         debut = datetime.now(timezone.utc) - timedelta(days=days)
#     debut_z = _z(debut)
#     cutoff = _z(debut - timedelta(seconds=window))     # évite de couper un incident en deux
#     lookback = max(CONTEXT_LOOKBACK, timedelta(minutes=context_minutes))
#     cutoff_ctx = _z(debut - lookback)

#     with ThreadPoolExecutor(max_workers=3) as ex:
#         f_dir = ex.submit(_directory_puis_crashs, creds, cutoff)
#         f_tel = ex.submit(fetch_device_telemetry, creds)
#         f_ctx = (ex.submit(fetch_context_events, creds, CONTEXT_EVENT_TYPES, cutoff_ctx)
#                  if with_context else None)
#         directory, activity, events = f_dir.result()
#         tel_by_dev = f_tel.result()
#         ctx = f_ctx.result() if f_ctx else {}

#     incidents = cluster_incidents(events, window)
#     add_sequence(incidents)
#     incidents = [i for i in incidents if i["time"] >= debut_z]   # garde seulement la fenêtre

#     boot_idx = build_boot_index(tel_by_dev)
#     status_idx = build_status_index(tel_by_dev)
#     ctx_idx = build_context_index(ctx)
#     for inc in incidents:
#         enrich(inc, boot_idx, ctx_idx, status_idx, tel_by_dev, activity, args)
#     return incidents

def directory_from_devices(dvc_list):
    """Reconstruit l'index 'directory' à partir de la liste déjà téléchargée par get_devices."""
    index = {}
    for d in dvc_list:
        dev_id = d.get("deviceId")
        if not dev_id:
            continue
        recent = d.get("recentUsers") or []
        index[dev_id] = {
            "deviceId": dev_id,
            "serial": d.get("serialNumber"),
            "model": d.get("model"),
            "osVersion": d.get("osVersion"),
            "orgUnit": d.get("orgUnitPath"),
            "status": d.get("status"),
            "lastUser": recent[0].get("email") if recent else None,
        }
    return index


def fetch_crash_sources(creds, debut=None, days=90, window=300,
                        context_minutes=60, with_context=True):
    """Appels Google des crashs et du contexte. Ne dépend pas des devices."""
    if debut is None:
        debut = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff = _z(debut - timedelta(seconds=window))      # évite de couper un incident en deux
    lookback = max(CONTEXT_LOOKBACK, timedelta(minutes=context_minutes))
    cutoff_ctx = _z(debut - lookback)

    with ThreadPoolExecutor(max_workers=2) as ex:
        f_crash = ex.submit(fetch_os_crash_events, creds, {}, cutoff)   # directory vide ici
        f_ctx = (ex.submit(fetch_context_events, creds, CONTEXT_EVENT_TYPES, cutoff_ctx)
                 if with_context else None)
        events, _raw = f_crash.result()
        ctx = f_ctx.result() if f_ctx else {}
    return events, ctx


def build_crash_incidents(events, ctx, dvc_list, telemetry_list, debut=None, days=90,
                          window=300, tz=3, context_minutes=60, context_count=5,
                          report_max_age=180):
    """Fusion, enrichissement et filtrage : aucun appel réseau."""
    if debut is None:
        debut = datetime.now(timezone.utc) - timedelta(days=days)
    debut_z = _z(debut)
    args = SimpleNamespace(
        days=days, window=window, tz=tz, context_minutes=context_minutes,
        context_count=context_count, report_max_age=report_max_age,
    )

    directory = directory_from_devices(dvc_list)
    tel_by_dev = {t["deviceId"]: t for t in telemetry_list if t.get("deviceId")}

    for e in events:                                    # même résultat que device_info(directory, ...)
        e.update(directory.get(e.get("deviceId")) or {})

    incidents = cluster_incidents(events, window)
    add_sequence(incidents)
    incidents = [i for i in incidents if i["time"] >= debut_z]   # garde seulement la fenêtre

    boot_idx = build_boot_index(tel_by_dev)
    status_idx = build_status_index(tel_by_dev)
    ctx_idx = build_context_index(ctx)
    for inc in incidents:
        enrich(inc, boot_idx, ctx_idx, status_idx, tel_by_dev, {}, args)   # {} = pas d'activité Directory
    return incidents

# if __name__ == "__main__":
#     credentials = get_credential()
#     main(credentials)
