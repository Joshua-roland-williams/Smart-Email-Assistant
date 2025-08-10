from .gemini_client import GeminiClient
from ..config.settings import Settings
from ..utils.logger import logger

class Summarizer:
    """
    Generates bullet-point summaries of emails using Gemini API.
    """
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.summary_prompt_template = Settings.SUMMARY_PROMPT

    async def summarize_email(self, email_thread: list) -> str:
        """
        Generates a summary for a given email thread.
        """
        thread_content = ""
        for email in email_thread:
            thread_content += f"From: {email['sender']}\n"
            thread_content += f"Subject: {email['subject']}\n"
            thread_content += f"Date: {email['date']}\n"
            thread_content += f"Body: {email['body']}\n\n"

        prompt = self.summary_prompt_template.format(email_thread=thread_content)
        summary = await self.gemini_client.generate_content(prompt)
        return summary if summary else "Could not generate summary."
