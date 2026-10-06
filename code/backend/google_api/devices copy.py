import os
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from backend.utils.save_to_file import save
from backend.utils.save_to_json import save_to_json
from backend.utils.format_date import format_date
from backend.utils.format_org import format_org_unit
from datetime import datetime, timedelta, timezone

def load_dotenv(*args, **kwargs):
    return False

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[3]
_token_env_path = os.getenv("GOOGLE_TOKEN_PATH", "credential/token.json")
_candidate_path = Path(_token_env_path) if Path(_token_env_path).is_absolute() else (BASE_DIR / _token_env_path).resolve()

if not _candidate_path.exists():
    _fallback = (BASE_DIR / "credential" / "token.json").resolve()
    TOKEN_FILE = _fallback if _fallback.exists() else _candidate_path
else:
    TOKEN_FILE = _candidate_path
OUTPUT_DIR = BASE_DIR / "output"

SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly",
    "https://www.googleapis.com/auth/chrome.management.telemetry.readonly",
    "https://www.googleapis.com/auth/admin.directory.customer.readonly",
    "https://www.googleapis.com/auth/admin.directory.user.readonly",
    "https://www.googleapis.com/auth/admin.reports.audit.readonly",
    "https://www.googleapis.com/auth/admin.reports.usage.readonly",
    # "https://www.googleapis.com/auth/chrome.management.reports.readonly"
    "https://www.googleapis.com/auth/admin.chrome.printers.readonly",
]

CUSTOMER_ID = os.getenv("GOOGLE_CUSTOMER_ID", "my_customer")

FIELDS = (
    "chromeosdevices(deviceId,serialNumber,model,status,osVersion,"
    "annotatedUser,lastEnrollmentTime,lastSync,recentUsers,"
    "lastKnownNetwork,orgUnitPath,annotatedLocation,macAddress,"
    "ethernetMacAddress,platformVersion,firmwareVersion)"
    ",nextPageToken"
)

def get_credentials():
    credentials = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not credentials.valid:
        credentials.refresh(Request())
    return credentials


def get_devices(credentials):
    service = build("admin", "directory_v1", credentials=credentials)

    all_devices = []
    page_token = None

    while True:
        response = service.chromeosdevices().list(
            customerId=CUSTOMER_ID,
            maxResults=10,
            pageToken=page_token,
            projection="FULL",
            fields=FIELDS
        ).execute()

        devices = response.get("chromeosdevices", [])
        for device in devices:
            device["lastSync"] = format_date(device.get("lastSync"))
            device["lastEnrollmentTime"] = format_date(
                device.get("lastEnrollmentTime")
            )
            device["orgUnitPath"] = format_org_unit(
                device.get("orgUnitPath")
            )
        all_devices.extend(devices)
        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return all_devices


# def format_device(device):
#     model = device.get("model", "Inconnu")
#     serial = device.get("serialNumber", "N/A")
#     status = device.get("status", "N/A")
#     os_version = device.get("osVersion", "N/A")
#     assigned_user = device.get("annotatedUser", "Non assigné")
#     last_sync = format_date(device.get("lastSync"))
#     org_unit = format_org_unit(device.get("orgUnitPath"))

#     recent_users = device.get("recentUsers", [])
#     last_user = recent_users[0].get("email", "N/A") if recent_users else "N/A"

#     last_networks = device.get("lastKnownNetwork", [])
#     last_ip = last_networks[0].get("ipAddress", "N/A") if last_networks else "N/A"

#     user_history = [u.get("email", "N/A") for u in recent_users[:5]]

#     lines = [
#         f"Appareil : {model} (S/N: {serial})",
#         f"   Statut: {status} | OS: {os_version}",
#         f"   Utilisateur assigné : {assigned_user}",
#         f"   Dernier utilisateur connecté : {last_user}",
#         f"   Dernière synchronisation : {last_sync}",
#         f"   Dernière adresse IP connue : {last_ip}",
#         f"   Unité organisationnelle : {org_unit}",
#         f"   Historique récent des utilisateurs : {', '.join(user_history) if user_history else 'Aucun'}",
#         "-" * 60,
#     ]
#     return "\n".join(lines)


# def print_devices(all_devices):
#     print(f"Nombre d'appareils : {len(all_devices)}\n")
#     print("=" * 60)
#     for device in all_devices:
#         print(format_device(device))


# ==============================================================
# À activer quand le privilège "Chrome Management > Lecture des
# données de télémétrie" sera accordé dans l'Admin Console.
# Nécessite : https://www.googleapis.com/auth/chrome.management.telemetry.readonly
# ==============================================================

def get_telemetry_devices(credentials):
    service_telemetry = build("chromemanagement", "v1", credentials=credentials)

    response = service_telemetry.customers().telemetry().devices().list(
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
        pageSize=50
    ).execute()

    return response.get("devices", [])

def get_telemetry_events(credentials):
    service_telemetry = build("chromemanagement", "v1", credentials=credentials)

    response = service_telemetry.customers().telemetry().events().list(
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


def get_print_audit_logs(credentials, days=30):
    """
    Récupère les événements d'impression depuis les applications
    Google Workspace (Docs, Sheets, Slides, Drive).
    Scope requis : admin.reports.audit.readonly (déjà dans SCOPES)
    """
    service = build("admin", "reports_v1", credentials=credentials)

    from datetime import datetime, timedelta, timezone
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
            events = item.get("events", [])
            for ev in events:
                if ev.get("name") != "print":
                    continue
                all_events.append({
                    "user": item.get("actor", {}).get("email"),
                    "time": item.get("id", {}).get("time"),
                    "ip": item.get("ipAddress"),
                    "documentId": ev.get("parameters", [{}])[0].get("value") if ev.get("parameters") else None,
                    "documentTitle": next(
                        (p["value"] for p in ev.get("parameters", [])
                         if p.get("name") == "doc_title"),
                        None
                    ),
                })

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return all_events

def get_print_audit_logs(credentials, days=30):
    """
    Récupère les événements d'impression depuis les applications
    Google Workspace (Docs, Sheets, Slides, Drive).
    """
    service = build("admin", "reports_v1", credentials=credentials)

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


# ==============================================================
# ✅ ÉTAPE 1 : Récupération des print jobs SANS filtre API
#    (contournement du bug "Invalid date/time string")
# Scope requis : chrome.management.reports.readonly
# ==============================================================

def get_print_jobs_report(credentials, page_size=100):
    """
    Récupère TOUS les travaux d'impression sans filtre.
    Le filtrage par date se fait côté Python (voir étape 2).
    """
    service = build("chromemanagement", "v1", credentials=credentials)

    all_print_jobs = []
    page_token = None

    while True:
        try:
            response = service.customers().reports().enumeratePrintJobs(
                customer="customers/my_customer",
                pageSize=page_size,
                pageToken=page_token,
                # ⚠️ Pas de filter, pas d'orderBy : bug API contourné
            ).execute()

            batch = response.get("printJobs", [])
            all_print_jobs.extend(batch)
            print(f"  → Page récupérée : {len(batch)} jobs "
                  f"(total cumulé : {len(all_print_jobs)})")

            page_token = response.get("nextPageToken")
            if not page_token:
                break
        except Exception as e:
            print(f"Erreur enumeratePrintJobs : {e}")
            break

    return all_print_jobs


def get_printers_summary(credentials, page_size=100):
    """
    Retourne un résumé par imprimante (nom, nombre d'impressions).
    Pas de filtre ici non plus pour éviter les bugs.
    """
    service = build("chromemanagement", "v1", credentials=credentials)

    all_printers = []
    page_token = None

    while True:
        try:
            response = service.customers().reports().countPrintJobsByPrinter(
                customer="customers/my_customer",
                pageSize=page_size,
                pageToken=page_token,
            ).execute()

            batch = response.get("printers", [])
            all_printers.extend(batch)
            print(f"  → Page imprimantes : {len(batch)} "
                  f"(total cumulé : {len(all_printers)})")

            page_token = response.get("nextPageToken")
            if not page_token:
                break
        except Exception as e:
            print(f"Erreur countPrintJobsByPrinter : {e}")
            break

    return all_printers


# ==============================================================
# ✅ ÉTAPE 2 : Filtrage côté Python
# ==============================================================

def filter_jobs_by_days(jobs, days=30):
    """
    Filtre les jobs pour ne garder que ceux des N derniers jours.
    Gère plusieurs formats de date possibles renvoyés par l'API.
    """
    limit = datetime.now(timezone.utc) - timedelta(days=days)
    recent = []

    for job in jobs:
        ts = job.get("completeTime") or job.get("createTime")
        if not ts:
            continue
        try:
            # Normalise "Z" en "+00:00" pour fromisoformat
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            continue
        if dt >= limit:
            recent.append(job)

    return recent

# ==============================================================
# ✅ Alternative : Lister les IMPRIMANTES CONFIGURÉES
#    Ne dépend PAS de la politique ReportDevicePrintJobs.
# Scope requis : admin.chrome.printers.readonly
# ==============================================================

def get_configured_printers(credentials, org_unit_id=None, page_size=100):
    """
    Liste les imprimantes configurées dans la console d'administration Google Workspace.
    
    Args:
        credentials: Credentials Google authentifiés.
        org_unit_id (str, optional): ID d'OU pour filtrer. Si None, retourne toutes les imprimantes.
        page_size (int): Nombre d'éléments par page (max 100).
    
    Returns:
        list: Liste de dictionnaires Printer (displayName, makeAndModel, uri, etc.)
    """
    service = build("admin", "directory_v1", credentials=credentials)

    all_printers = []
    page_token = None

    while True:
        try:
            params = {
                "parent": f"customers/{CUSTOMER_ID}",
                "pageSize": page_size,
                "pageToken": page_token,
            }
            # Filtrer par OU si fourni
            if org_unit_id:
                params["orgUnitId"] = org_unit_id

            response = service.customers().chrome().printers().list(**params).execute()

            batch = response.get("printers", [])
            all_printers.extend(batch)
            print(f"  → Page imprimantes : {len(batch)} (total cumulé : {len(all_printers)})")

            page_token = response.get("nextPageToken")
            if not page_token:
                break
        except Exception as e:
            print(f"Erreur printers.list : {e}")
            break

    return all_printers

# ==============================================================
# MAIN — Tests
# ==============================================================

if __name__ == "__main__":
    creds = get_credentials()
    devices = get_devices(creds)
    print(f"✅ {len(devices)} devices récupérés")

    # --- ÉTAPE 1 : récupération brute sans filtre ---
    print("\n--- ÉTAPE 1 : Récupération de TOUS les print jobs (sans filtre) ---")
    print_jobs = get_print_jobs_report(creds)
    print(f"\nTotal jobs bruts récupérés : {len(print_jobs)}")

    print("\n--- Récupération du résumé par imprimante ---")
    summary = get_printers_summary(creds)
    print(f"\nNombre d'imprimantes distinctes : {len(summary)}")

    if summary:
        print("\nListe des imprimantes :")
        for p in summary:
            name = p.get("printer", "?")
            count = p.get("jobCount", 0)
            users = p.get("userCount", 0)
            print(f"   • {name}  ({count} jobs, {users} users)")

    # --- ÉTAPE 2 : filtrage côté Python ---
    print("\n--- ÉTAPE 2 : Filtrage des jobs sur les 30 derniers jours ---")
    recent_jobs = filter_jobs_by_days(print_jobs, days=30)
    print(f"Jobs des 30 derniers jours : {len(recent_jobs)}")

    if recent_jobs:
        print("\nDétail des jobs récents :")
        for job in recent_jobs:
            printer_name = job.get("printer", "?")
            user_email = job.get("userEmail", "?")
            job_title = job.get("title", "?")
            complete_time = job.get("completeTime", "?")
            page_count = job.get("documentPageCount", 0)
            print(f"   Imprimante  : {printer_name}")
            print(f"   Utilisateur : {user_email}")
            print(f"   Document    : {job_title}")
            print(f"   Pages       : {page_count}")
            print(f"   Date        : {complete_time}")
            print("   " + "-" * 36)

    # --- Sauvegarde ---
    if print_jobs:
        save(print_jobs, "print_jobs_report",
             "Rapport détaillé des travaux d'impression", formatter=str)
        save_to_json(print_jobs, "print_jobs_report")
    if summary:
        save(summary, "printers_summary",
             "Résumé par imprimante", formatter=str)
        save_to_json(summary, "printers_summary")

    # --- Diagnostic ---
    print("\n--- Diagnostic ---")
    if not print_jobs and not summary:
        print("⚠️  Aucun job ni imprimante retourné. Causes possibles :")
        print("   1. Politique 'ReportDevicePrintJobs' non activée dans")
        print("      la console d'administration Google Workspace")
        print("   2. Scope 'chrome.management.reports.readonly' non autorisé")
        print("      (re-authentifier l'application OAuth)")
        print("   3. Aucun travail d'impression enregistré récemment")
    elif not print_jobs and summary:
        print("ℹ️  Résumé imprimantes OK mais détail jobs vide.")
        print("   Le détail remonte probablement avec un délai.")
    else:
        print("✅ Données récupérées avec succès.")
        
        print("\n--- Imprimantes configurées dans la console d'administration ---")
    configured_printers = get_configured_printers(creds)
    print(f"\nTotal imprimantes configurées : {len(configured_printers)}")

    if configured_printers:
        print("\nListe des imprimantes configurées :")
        for p in configured_printers:
            display_name = p.get("displayName", "?")
            model = p.get("makeAndModel", "?")
            uri = p.get("uri", "?")
            org_unit = p.get("orgUnitId", "?")
            print(f"   • {display_name}")
            print(f"       Modèle : {model}")
            print(f"       URI    : {uri}")
            print(f"       OU     : {org_unit}")
            print("   " + "-" * 36)

        # Sauvegarde
        save(configured_printers, "configured_printers",
             "Imprimantes configurées", formatter=str)
        save_to_json(configured_printers, "configured_printers")
    else:
        print("Aucune imprimante configurée trouvée (ou scope manquant).")

# if __name__ == "__main__":
#     creds = get_credentials()
#     devices = get_devices(creds)
# #     # print_devices(devices)
#     print_logs = get_print_audit_logs(creds, days=30)
#     for log in print_logs:
#         print(f"{log['time']} | {log['user']} | {log['documentTitle']}")
#     save(print_logs, "printer_log", "Télémétrie Log Printer", formatter=str)
#     save_to_json(print_logs, "printer_log")

# def get_printers_summary(credentials):
#     """
#     Retourne un résumé par imprimante (nom, nombre d'impressions, etc.)
#     """
#     service = build("chromemanagement", "v1", credentials=credentials)
    
#     try:
#         response = service.customers().reports().countPrintJobsByPrinter(
#             customer="customers/my_customer",
#             pageSize=100,
#         ).execute()
        
#         return response.get("printers", [])
#     except Exception as e:
#         print(f"Erreur: {e}")
#         return []
    
# def get_print_jobs_report(credentials, page_size=100):
#     service = build("chromemanagement", "v1", credentials=credentials)
    
#     all_print_jobs = []
#     page_token = None
    
#     while True:
#         try:
#             response = service.customers().reports().enumeratePrintJobs(
#                 customer="customers/my_customer",
#                 pageSize=page_size,
#                 pageToken=page_token,
#             ).execute()
            
#             all_print_jobs.extend(response.get("printJobs", []))
#             page_token = response.get("nextPageToken")
#             if not page_token:
#                 break
#         except Exception as e:
#             print(f"Erreur: {e}")
#             break
    
#     return all_print_jobs


# if __name__ == "__main__":
#     creds = get_credentials()
#     devices = get_devices(creds)
    
#     # --- Test du nouveau rapport d'impression détaillé ---
#     print("\n--- Récupération du rapport détaillé des travaux d'impression ---")
#     print_jobs = get_print_jobs_report(creds) # Test sur les 7 derniers jours
#     summary = get_printers_summary(creds)
    
#     limit = datetime.now(timezone.utc) - timedelta(days=30)

#     recent_jobs = [
#         j for j in print_jobs
#         if datetime.fromisoformat(j["completeTime"].replace("Z", "+00:00")) >= limit
#     ]
    
#     print(summary)
    
#     if print_jobs:
#         print(f"Nombre de travaux d'impression récupérés : {len(print_jobs)}\n")
#         # Afficher les informations clés pour chaque travail d'impression
#         for job in print_jobs:
#             # Extraire les informations pertinentes de la réponse
#             printer_name = job.get("printer", "Nom d'imprimante inconnu")
#             user_email = job.get("userEmail", "Email inconnu")
#             job_title = job.get("title", "Titre inconnu")
#             complete_time = job.get("completeTime", "Date inconnue")
#             page_count = job.get("documentPageCount", 0)
            
#             print(f"Imprimante : {printer_name}")
#             print(f"   Utilisateur : {user_email}")
#             print(f"   Document    : {job_title}")
#             print(f"   Pages       : {page_count}")
#             print(f"   Date        : {complete_time}")
#             print("-" * 40)
            
            
#         # Sauvegarder les résultats comme pour les autres appels
#         save(print_jobs, "print_jobs_report", "Rapport détaillé des travaux d'impression", formatter=str)
#         save_to_json(print_jobs, "print_jobs_report")
#     else:
#         print("Aucun travail d'impression trouvé ou accès à l'API non autorisé.")
#         print("Vérifiez que le scope 'chrome.management.reports.readonly' est bien autorisé dans votre console d'administration Google Workspace.")
        
#     # À décommenter quand le privilège télémétrie est accordé :
#     device = get_devices(creds)
#     save(device,'device',"Telemetrie appareil ",formatter=str)
#     telemetry_devices = get_telemetry_devices(creds)
#     telemetry_events = get_telemetry_events(creds)
#     save(telemetry_devices, "telemetry_devices", "Télémétrie - Appareils", formatter=str)
#     save_to_json(telemetry_devices, "telemetry_devices")
#     save(telemetry_events, "telemetry_events", "Télémétrie - Événements", formatter=str)
#     save_to_json(telemetry_events, "telemetry_events")

