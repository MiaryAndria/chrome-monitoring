from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
def get_credentials(TOKEN_FILE,SCOPES):
    credentials = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not credentials.valid:
        credentials.refresh(Request())
    return credentials