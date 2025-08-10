from smart_email_assistant.backend.src.ai.gemini_client import GeminiClient
from smart_email_assistant.backend.src.config.settings import Settings

class Summarizer:
    """
    Generates bullet-point summaries of emails using Gemini API.
    """
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.summary_prompt_template = Settings.SUMMARY_PROMPT

    def summarize_email(self, subject: str, sender: str, body: str) -> str:
        """
        Generates a summary for a given email.
        """
        prompt = Settings.SUMMARY_PROMPT.format(subject=subject, sender=sender, body=body)
        summary = self.gemini_client.generate_content(prompt)
        return summary if summary else "Could not generate summary."
