import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

class GmailClient:
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
                token.write(creds.to_json())

        return build("gmail", "v1", credentials=creds)
    

    def search_emails(self, query, max_results = 20):
        """
        Search Gmail for emails matching a query.

        Args:
            query: Gmail search query e.g. 'has:attachment subject:resume'
            max_results: maximum number of emails to fetch
        """

        results = self.service.users().messages().list(
            userId="me",
            q=query,
            maxResults=max_results
        ).execute()

        messages = results.get("messages", [])
        emails = []

        for msg in messages:
            detail = self.service.users().messages().get(
                userId="me",
                id=msg["id"],
                format="full"
            ).execute()

            headers = {
                h["name"]: h["value"]
                for h in detail["payload"]["headers"]
            }

            attachments = []
            for part in detail["payload"].get("parts", []):
                filename = part.get("filename", "")

                if filename.lower().endswith((".pdf", ".docx")):
                    attachments.append({
                        "filename": filename,
                        "attachment_id": part["body"].get("attachmentId"),
                        "mime_type": part.get("mimeType")
                    })

            if attachments:
                emails.append({
                    "id": msg["id"],
                    "from": headers.get("From", ""),
                    "subject": headers.get("Subject", ""),
                    "date": headers.get("Date", ""),
                    "attachments": attachments
                })

        return emails
    
    def download_attachment(self, messages_id, attachment_id):
        """
        Download an email attachment and return its raw bytes.

        Args:
            message_id: the email's ID
            attachment_id: the attachment's ID within that email
        """

        attachment = self.service.users().messages().attachments().get(
            userId="me",
            messageId=messages_id,
            id=attachment_id
        ).execute()

        return base64.urlsafe_b64decode(attachment["data"])