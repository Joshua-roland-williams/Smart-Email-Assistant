from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from smart_email_assistant.backend.src.auth.gmail_auth import GmailAuth
from smart_email_assistant.backend.src.config.settings import Settings
import base64
import email
from datetime import datetime, timedelta

class GmailClient:
    """
    Wrapper for Gmail API interactions.
    """
    def __init__(self):
        self.auth = GmailAuth()
        self.service = self._build_service()

    def _build_service(self):
        """Builds and returns the Gmail API service."""
        creds = self.auth.authenticate()
        return build('gmail', 'v1', credentials=creds)

    def get_user_profile(self):
        """Fetches the user's Gmail profile."""
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def list_messages(self, query=''):
        """Lists messages from the user's inbox."""
        try:
            response = self.service.users().messages().list(userId='me', q=query).execute()
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])
            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = self.service.users().messages().list(userId='me', q=query, pageToken=page_token).execute()
                messages.extend(response['messages'])
            return messages
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def get_message(self, msg_id):
        """Retrieves a specific message by ID."""
        try:
            message = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            return message
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def get_messages_from_last_n_days(self, days=Settings.DAYS_TO_PROCESS):
        """Fetches emails from the last N days."""
        date_cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')
        query = f'after:{date_cutoff}'
        message_ids = self.list_messages(query=query)
        emails = []
        for msg_id in message_ids:
            email_data = self.get_message(msg_id['id'])
            if email_data:
                emails.append(email_data)
        return emails

    def get_thread(self, thread_id):
        """Retrieves a specific thread by ID."""
        try:
            thread = self.service.users().threads().get(userId='me', id=thread_id).execute()
            return thread
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def send_message(self, message):
        """Sends an email message."""
        try:
            sent_message = self.service.users().messages().send(userId='me', body=message).execute()
            print(f"Message Id: {sent_message['id']}")
            return sent_message
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
