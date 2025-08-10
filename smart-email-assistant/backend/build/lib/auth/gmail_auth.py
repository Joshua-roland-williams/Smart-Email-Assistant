import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from smart_email_assistant.backend.src.config.settings import Settings

class GmailAuth:
    """
    Handles OAuth2 authentication for Gmail API.
    """
    def __init__(self):
        self.scopes = Settings.GMAIL_SCOPES
        self.credentials_file = os.path.join(os.path.dirname(__file__), '..', Settings.CREDENTIALS_FILE)
        self.token_file = os.path.join(os.path.dirname(__file__), '..', Settings.TOKEN_FILE)
        self.creds = None

    def authenticate(self):
        """
        Authenticates with Gmail API using OAuth2.
        Loads existing token or initiates new flow.
        """
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.scopes)
                self.creds = flow.run_local_server(port=0)
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)
        return self.creds
