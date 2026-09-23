from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).resolve().parents[3]
TOKEN_FILE = BASE_DIR / "credential" / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly",
    "https://www.googleapis.com/auth/admin.directory.customer.readonly",
    "https://www.googleapis.com/auth/admin.directory.user.readonly",
    "https://www.googleapis.com/auth/admin.reports.audit.readonly",
    "https://www.googleapis.com/auth/admin.reports.usage.readonly",
    "https://www.googleapis.com/auth/chrome.management.telemetry.readonly",
]

credentials = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

service_directory = build("admin", "directory_v1", credentials=credentials)

response = service_directory.chromeosdevices().list(
    customerId="my_customer",
    maxResults=10
).execute()
print(response)