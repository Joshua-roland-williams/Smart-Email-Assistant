from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from ..auth.gmail_auth import GmailAuth
from ..config.settings import Settings
import base64
import email
from datetime import datetime, timedelta
from fastapi import HTTPException, status # Import HTTPException and status
from ..utils.logger import logger

class GmailClient:
    """
    Wrapper for Gmail API interactions.
    """
    def __init__(self):
        self.auth = GmailAuth()
        self._service = None # Defer service building

    def _get_service(self):
        """Gets or builds the Gmail API service, authenticating if necessary."""
        if self._service is None:
            try:
                creds = self.auth.authenticate() # This is where authentication is triggered
                self._service = build('gmail', 'v1', credentials=creds)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Google authentication failed: {e}. Please ensure your credentials.json is correct and you have authenticated."
                )
        return self._service

    def get_user_profile(self):
        """Fetches the user's Gmail profile."""
        service = self._get_service()
        try:
            profile = service.users().getProfile(userId='me').execute()
            return profile
        except HttpError as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve user profile from Gmail API: {error}"
            )

    def list_messages(self, query=''):
        """Lists messages from the user's inbox."""
        service = self._get_service()
        try:
            response = service.users().messages().list(userId='me', q=query).execute()
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])
            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = service.users().messages().list(userId='me', q=query, pageToken=page_token).execute()
                messages.extend(response['messages'])
            return messages
        except HttpError as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list messages from Gmail API: {error}"
            )

    def get_message(self, msg_id):
        """Retrieves a specific message by ID."""
        service = self._get_service()
        try:
            message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            return message
        except HttpError as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve message {msg_id} from Gmail API: {error}"
            )

    def get_messages_from_last_n_days(self, days=Settings.DAYS_TO_PROCESS):
        """Fetches emails from the last N days."""
        date_cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')
        query = f'after:{date_cutoff}'
        try:
            message_ids = self.list_messages(query=query)
            emails = []
            for msg_id in message_ids:
                email_data = self.get_message(msg_id['id'])
                if email_data:
                    emails.append(email_data)
            return emails
        except HttpError as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch messages from last {days} days from Gmail API: {error}"
            )

    def get_messages_for_today(self):
        """Fetches emails received on the current date."""
        today = datetime.now().strftime('%Y/%m/%d')
        query = f'after:{today} before:{(datetime.now() + timedelta(days=1)).strftime("%Y/%m/%d")}'
        try:
            message_ids = self.list_messages(query=query)
            emails = []
            for msg_id in message_ids:
                email_data = self.get_message(msg_id['id'])
                if email_data:
                    emails.append(email_data)
            return emails
        except HttpError as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch messages for today from Gmail API: {error}"
            )

    def get_thread(self, thread_id):
        """Retrieves a specific thread by ID."""
        service = self._get_service()
        try:
            thread = service.users().threads().get(userId='me', id=thread_id).execute()
            return thread
        except HttpError as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve thread {thread_id} from Gmail API: {error}"
            )

    def send_message(self, message):
        """Sends an email message."""
        service = self._get_service()
        try:
            sent_message = service.users().messages().send(userId='me', body=message).execute()
            return sent_message
        except HttpError as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send message via Gmail API: {error}"
            )
