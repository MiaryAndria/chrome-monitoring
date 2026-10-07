import os
import time
from pathlib import Path

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from backend.utils.format_date import format_date
from backend.utils.format_org import format_org_unit
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

# ==============================================================
# AUTHENTIFICATION
# ==============================================================

def get_credential():
    return get_credentials(TOKEN_FILE, SCOPES)


credentials = get_credential()


# ==============================================================
# RÉCUPÉRATION DES DEVICES
# ==============================================================
def _execute_with_retry(request_fn, max_retries=4, base_delay=1.0):
    for attempt in range(max_retries + 1):
        try:
            return request_fn()
        except HttpError as exc:
            status = getattr(getattr(exc, "resp", None), "status", None)
            if status not in (429, 500, 502, 503, 504) or attempt >= max_retries:
                raise

            delay = base_delay * (2 ** attempt)
            print(
                f"[Google API retry] status={status}, attempt={attempt + 1}/{max_retries + 1}, "
                f"retrying in {delay:.1f}s"
            )
            time.sleep(delay)


def get_devices(credentials):
    service = build("admin", "directory_v1", credentials=credentials,
                    cache_discovery=False)

    all_devices = []
    page_token = None

    while True:
        response = _execute_with_retry(
            lambda: service.chromeosdevices().list(
                customerId=CUSTOMER_ID,
                maxResults=100,
                pageToken=page_token,
                projection="FULL",
                fields=FIELDS,
            ).execute()
        )

        for device in response.get("chromeosdevices", []):
            device["lastSync"] = format_date(device.get("lastSync"))
            device["lastEnrollmentTime"] = format_date(
                device.get("lastEnrollmentTime")
            )
            device["orgUnitPath"] = format_org_unit(
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
        response = _execute_with_retry(
            lambda: service.customers().telemetry().devices().list(
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
        )

        batch = response.get("devices", [])
        all_devices.extend(batch)
        print(f"  → Page télémétrie : {len(batch)} devices "
              f"(total : {len(all_devices)})")

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return all_devices



# ==============================================================
# MAIN
# ==============================================================

if __name__ == "__main__":
    creds = get_credential()

    devices = get_devices(creds)
    telemetry_devices = get_telemetry_devices(creds)

    print("--- Récupération des devices ---")
    print(f"✅ {len(devices)} devices récupérés\n")

    print("--- Récupération de la télémétrie (périphériques USB) ---")
    print(f"✅ {len(telemetry_devices)} télémetry devices récupérés\n")
