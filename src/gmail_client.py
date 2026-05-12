import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

class GmailClients():
    """Connects to Gmail and fetches emails with attachments."""

    def __init__(self):
        self.service = self._authenticate()

    def _authenticate(self):
        """
        Handle Gmail authentication.
        First time: opens browser for Google login.
        After that: uses saved token.json automatically.
        """
        creds = None

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            with open("token.json", "w") as token:
                token. write(creds.to_json())

        return build("gmail", "v1", credentials=creds)
    
    