# from pathlib import Path
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.oauth2.credentials import Credentials
# from google.auth.transport.requests import Request


# BASE_DIR = Path(__file__).resolve().parents[3]

# CREDENTIALS_FILE = BASE_DIR / "credential" / "credential.json"
# TOKEN_FILE = BASE_DIR / "credential" / "token.json"


# SCOPES = [
#     "https://www.googleapis.com/auth/chrome.management.telemetry.readonly",
#     "https://www.googleapis.com/auth/chrome.management.reports.readonly",
#     "https://www.googleapis.com/auth/admin.chrome.printers.readonly",
#     "https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly",
#     "https://www.googleapis.com/auth/admin.directory.customer.readonly",
#     "https://www.googleapis.com/auth/admin.directory.user.readonly",
#     "https://www.googleapis.com/auth/admin.reports.audit.readonly",
#     "https://www.googleapis.com/auth/admin.reports.usage.readonly",
# ]


# def get_credentials():

#     credentials = None

#     if TOKEN_FILE.exists():
#         credentials = Credentials.from_authorized_user_file(
#             TOKEN_FILE,
#             SCOPES
#         )

#     if not credentials or not credentials.valid:
        
#         if credentials and credentials.expired and credentials.refresh_token:
#             credentials.refresh(Request())

#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 CREDENTIALS_FILE,
#                 SCOPES
#             )

#             credentials = flow.run_local_server(port=0)
#         TOKEN_FILE.write_text(credentials.to_json())

#     return credentials