import google.generativeai as genai
from ..config.settings import Settings
from ..auth.credentials_manager import CredentialsManager
from ..utils.rate_limiter import RateLimiter
from ..utils.logger import logger
import time
import asyncio
import random
import re

class GeminiClient:
    """
    Handles interactions with the Google Gemini API.
    """
    def __init__(self):
        self.api_key = CredentialsManager().get_gemini_api_key()
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(Settings.GEMINI_MODEL)
        self.rate_limiter = RateLimiter(rate_limit=5, interval=60) # 5 calls per minute

    async def generate_content(self, prompt: str, max_retries: int = 5):
        """
        Generates content using the configured Gemini model with retry logic.
        """
        for attempt in range(max_retries):
            await self.rate_limiter.wait_for_permission()
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                error_message = str(e)
                print(f"Error generating content with Gemini API (Attempt {attempt + 1}/{max_retries}): {error_message}")
                if "429" in error_message and attempt < max_retries - 1:
                    # Extract retry delay from error message if available, otherwise use exponential backoff
                    retry_delay_match = re.search(r"retry_delay \{\s*seconds: (\d+)", error_message)
                    if retry_delay_match:
                        delay = int(retry_delay_match.group(1))
                    else:
                        delay = 2 ** attempt + random.uniform(0, 1)
                    print(f"Retrying in {delay:.2f} seconds...")
                    await asyncio.sleep(delay)
                else:
                    return None
        return None # All retries failed
