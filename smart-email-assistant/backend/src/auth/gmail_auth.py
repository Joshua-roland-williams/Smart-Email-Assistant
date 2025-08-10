import os
import pickle
from fastapi import HTTPException, status # Import HTTPException and status
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from ..config.settings import Settings
import pickle
import os
from ..utils.logger import logger

class GmailAuth:
    """
    Handles OAuth2 authentication for Gmail API.
    """
    def __init__(self):
        self.scopes = Settings.GMAIL_SCOPES
        self.credentials_file = os.path.join(os.path.dirname(__file__), '..', 'config', Settings.CREDENTIALS_FILE)
        self.token_file = os.path.join(os.path.dirname(__file__), '..', 'config', Settings.TOKEN_FILE)
        self.creds = None

    def authenticate(self):
        """
        Authenticates with Gmail API using OAuth2.
        Loads existing token or raises an error if authentication is required.
        """
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Failed to refresh Google access token: {e}. Please re-authenticate."
                    )
            else:
                # For web applications, the authentication flow should be initiated from the frontend
                # and handled via a redirect. This backend part should not open a local server.
                # Instead, it should indicate that authentication is needed.
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Google authentication required. Please initiate the OAuth2 flow from the frontend."
                )
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)
        return self.creds
