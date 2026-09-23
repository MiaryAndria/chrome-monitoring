import os
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
# from backend.utils.save_to_file import save
# from backend.utils.save_to_json import save_to_json
from backend.utils.format_date import format_date
from backend.utils.format_org import format_org_unit

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[3]
_token_env_path = os.getenv("GOOGLE_TOKEN_PATH", "../credential/token.json")
TOKEN_FILE = Path(_token_env_path) if Path(_token_env_path).is_absolute() else (BASE_DIR / _token_env_path).resolve()
OUTPUT_DIR = BASE_DIR / "output"

SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly",
    "https://www.googleapis.com/auth/chrome.management.telemetry.readonly",
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


# if __name__ == "__main__":
#     creds = get_credentials()
#     devices = get_devices(creds)
#     # print_devices(devices)

#     # À décommenter quand le privilège télémétrie est accordé :
#     device = get_devices(creds)
#     save(device,'device',"Telemetrie appareil ",formatter=str)
#     telemetry_devices = get_telemetry_devices(creds)
#     telemetry_events = get_telemetry_events(creds)
#     save(telemetry_devices, "telemetry_devices", "Télémétrie - Appareils", formatter=str)
#     save_to_json(telemetry_devices, "telemetry_devices")
#     save(telemetry_events, "telemetry_events", "Télémétrie - Événements", formatter=str)
#     save_to_json(telemetry_events, "telemetry_events")
