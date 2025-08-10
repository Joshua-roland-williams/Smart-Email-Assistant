from smart_email_assistant.backend.src.ai.gemini_client import GeminiClient
from smart_email_assistant.backend.src.config.settings import Settings

class ReplyGenerator:
    """
    Generates professional email reply drafts using Gemini API.
    """
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.reply_prompt_template = Settings.REPLY_PROMPT

    def generate_reply(self, subject: str, sender: str, body: str) -> str:
        """
        Generates a reply draft for a given email.
        """
        prompt = Settings.REPLY_PROMPT.format(subject=subject, sender=sender, body=body)
        reply_draft = self.gemini_client.generate_content(prompt)
        return reply_draft if reply_draft else "Could not generate reply draft."
