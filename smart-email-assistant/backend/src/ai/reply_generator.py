from .gemini_client import GeminiClient
from ..config.settings import Settings
from ..utils.logger import logger

class ReplyGenerator:
    """
    Generates professional email reply drafts using Gemini API.
    """
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.reply_prompt_template = Settings.REPLY_PROMPT

    async def generate_reply(self, email_thread: list, recipient: str, instructions: str = "Generate a professional and concise reply.") -> str:
        """
        Generates a reply draft for a given email thread.
        """
        thread_content = ""
        for email in email_thread:
            thread_content += f"From: {email['sender']}\n"
            thread_content += f"Subject: {email['subject']}\n"
            thread_content += f"Date: {email['date']}\n"
            thread_content += f"Body: {email['body']}\n\n"

        prompt = self.reply_prompt_template.format(email_thread=thread_content, instructions=instructions)
        reply_draft = await self.gemini_client.generate_content(prompt)
        
        if reply_draft:
            # Assuming the last email in the thread is the one being replied to
            original_email_id = email_thread[-1]['id'] if email_thread else 'N/A'
            logger.log_response(original_email_id, reply_draft, recipient)
            return reply_draft
        else:
            return "Could not generate reply draft."
