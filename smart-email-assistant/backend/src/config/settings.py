import os
from dotenv import load_dotenv
from ..utils.logger import logger

load_dotenv()

class Settings:
    # Gmail API
    GMAIL_SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send'
    ]
    CREDENTIALS_FILE = "credentials.json"
    TOKEN_FILE = "token.json" # Added for token storage

    # Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = "gemini-2.0-flash"

    # Processing
    MAX_EMAILS_PER_BATCH = 50
    DAYS_TO_PROCESS = 7
    ENABLE_REPLY_GENERATION = True

    # Export
    CSV_OUTPUT_PATH = "output/emails_{timestamp}.csv"
    INCLUDE_EMAIL_CONTENT = False  # Privacy setting

    # Server
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    GOOGLE_REDIRECT_URI = "http://localhost:8000/api/auth/google/callback" # Must match authorized redirect URI in Google Cloud Console
    FRONTEND_REDIRECT_URI_AFTER_AUTH = "http://localhost:5173" # Frontend URL to redirect to after successful auth

    # AI Prompts
    SUMMARY_PROMPT = """
    You are an AI assistant specialized in summarizing email threads.
    Your goal is to provide a concise and informative summary of the given email thread.
    Focus on the main topic, key decisions, action items, and important details.
    Keep the summary under 200 words.

    Email Thread:
    {email_thread}
    """

    REPLY_PROMPT = """
    You are an AI assistant specialized in generating email replies.
    Your goal is to craft a concise and appropriate reply based on the given email thread and the user's instructions.
    Consider the context of the conversation and maintain a professional tone.

    Email Thread:
    {email_thread}

    User Instructions:
    {instructions}
    """
