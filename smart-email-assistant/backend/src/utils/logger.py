import logging
import os
from datetime import datetime

class AppLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger('SmartEmailAssistant')
        logger.setLevel(logging.INFO)

        # Create handlers
        current_date = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(self.log_dir, f"app_{current_date}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')

        # Create formatters and add it to handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        return logger

    def log_email(self, email_data):
        self.logger.info(f"EMAIL_RECEIVED: ID={email_data.get('id')}, Subject='{email_data.get('subject')}', Sender='{email_data.get('sender')}', Date='{email_data.get('date')}', Snippet='{email_data.get('snippet')}'")
        self.logger.debug(f"EMAIL_BODY: {email_data.get('body')}")

    def log_response(self, original_email_id, response_text, recipient):
        self.logger.info(f"EMAIL_RESPONSE_SENT: OriginalEmailID={original_email_id}, Recipient='{recipient}', Response='{response_text}'")

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)

# Global logger instance
logger = AppLogger()
