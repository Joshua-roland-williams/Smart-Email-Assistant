import google.generativeai as genai
from smart_email_assistant.backend.src.config.settings import Settings
from smart_email_assistant.backend.src.auth.credentials_manager import CredentialsManager

class GeminiClient:
    """
    Handles interactions with the Google Gemini API.
    """
    def __init__(self):
        self.api_key = CredentialsManager().get_gemini_api_key()
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(Settings.GEMINI_MODEL)

    def generate_content(self, prompt: str):
        """
        Generates content using the configured Gemini model.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating content with Gemini API: {e}")
            return None
