import os
import json
from smart_email_assistant.backend.src.config.settings import Settings

class CredentialsManager:
    """
    Handles secure storage and retrieval of application credentials.
    """
    def __init__(self):
        self.credentials_file = os.path.join(os.path.dirname(__file__), Settings.CREDENTIALS_FILE)

    def load_credentials(self):
        """
        Loads client credentials from the specified JSON file.
        """
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(f"Credentials file not found at {self.credentials_file}. "
                                    "Please ensure config/credentials.json is present.")
        with open(self.credentials_file, 'r') as f:
            return json.load(f)

    def save_credentials(self, credentials):
        """
        Saves client credentials to the specified JSON file.
        """
        with open(self.credentials_file, 'w') as f:
            json.dump(credentials, f, indent=4)

    def get_gemini_api_key(self):
        """
        Retrieves the Gemini API key from environment variables.
        """
        api_key = Settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. "
                             "Please set it in your .env file or system environment.")
        return api_key
