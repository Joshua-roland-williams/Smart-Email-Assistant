import os
from .config.settings import Settings
from .auth.gmail_auth import GmailAuth
from .email.gmail_client import GmailClient
from .email.email_processor import EmailProcessor
from .email.thread_analyzer import ThreadAnalyzer
from .ai.summarizer import Summarizer
from .ai.reply_generator import ReplyGenerator
from .utils.data_processor import DataProcessor
from .utils.csv_exporter import CSVExporter
from .utils.rate_limiter import RateLimiter
from fastapi import HTTPException, status
import json
import logging
from .utils.logger import logger as app_logger

# Configure logging for extensive details
# The app_logger instance from utils.logger will handle file and console logging.
# We can still use a basic logger for main.py specific debugs if needed, but
# the primary application logs will go through app_logger.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # Set level for this specific logger if needed

class SmartEmailAssistant:
    """
    Main application class for the Smart Email Assistant.
    Orchestrates email processing, AI summarization, reply generation, and data export.
    """
    def __init__(self):
        self.gmail_client = GmailClient()
        self.email_processor = EmailProcessor()
        self.summarizer = Summarizer()
        self.reply_generator = ReplyGenerator()
        self.data_processor = DataProcessor()
        self.csv_exporter = CSVExporter()
        
        # Defer authentication and user profile retrieval
        self.user_email_address = None
        self.thread_analyzer = None # Will be initialized after successful authentication

        self.rate_limiter = RateLimiter(rate_limit=10, interval=60) # 10 calls per minute example

    async def process_emails(self):
        """
        Fetches, processes, summarizes, and generates replies for emails.
        """
        app_logger.debug("Starting email processing.")
        # Ensure user_email_address and thread_analyzer are initialized
        if not self.user_email_address or not self.thread_analyzer:
            app_logger.info("User email address or thread analyzer not initialized. Attempting deferred initialization.")
            try:
                user_profile = self.gmail_client.get_user_profile()
                self.user_email_address = user_profile['emailAddress'] if user_profile else None
                if not self.user_email_address:
                    app_logger.error("Could not retrieve user email address. Authentication required.")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required: Could not retrieve user email address. Please ensure you have authenticated with Google."
                    )
                self.thread_analyzer = ThreadAnalyzer(self.user_email_address)
                app_logger.info(f"SmartEmailAssistant initialized for user: {self.user_email_address}")
            except HTTPException as e:
                app_logger.error(f"HTTPException during deferred SmartEmailAssistant initialization: {e.detail}", exc_info=True)
                raise e # Re-raise the HTTPException
            except Exception as e:
                app_logger.error(f"Unexpected error during deferred SmartEmailAssistant initialization: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Backend initialization failed during email processing: {e}. Please check your Google API credentials and authentication."
                )

        app_logger.info(f"Fetching emails from the last {Settings.DAYS_TO_PROCESS} days...")
        raw_emails = self.gmail_client.get_messages_from_last_n_days(Settings.DAYS_TO_PROCESS)
        app_logger.info(f"Found {len(raw_emails)} raw emails.")
        app_logger.debug(f"Raw emails fetched: {[e.get('id') for e in raw_emails]}")

        processed_emails = []
        email_threads = {} # Group emails by threadId

    async def process_emails_for_today(self):
        """
        Fetches, processes, summarizes, and generates replies for emails received on the current date.
        """
        app_logger.debug("Starting email processing for today.")
        # Ensure user_email_address and thread_analyzer are initialized
        if not self.user_email_address or not self.thread_analyzer:
            app_logger.info("User email address or thread analyzer not initialized. Attempting deferred initialization.")
            try:
                user_profile = self.gmail_client.get_user_profile()
                self.user_email_address = user_profile['emailAddress'] if user_profile else None
                if not self.user_email_address:
                    app_logger.error("Could not retrieve user email address. Authentication required.")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required: Could not retrieve user email address. Please ensure you have authenticated with Google."
                    )
                self.thread_analyzer = ThreadAnalyzer(self.user_email_address)
                app_logger.info(f"SmartEmailAssistant initialized for user: {self.user_email_address}")
            except HTTPException as e:
                app_logger.error(f"HTTPException during deferred SmartEmailAssistant initialization: {e.detail}", exc_info=True)
                raise e # Re-raise the HTTPException
            except Exception as e:
                app_logger.error(f"Unexpected error during deferred SmartEmailAssistant initialization: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Backend initialization failed during email processing: {e}. Please check your Google API credentials and authentication."
                )

        app_logger.info("Fetching emails for today...")
        raw_emails = self.gmail_client.get_messages_for_today()
        app_logger.info(f"Found {len(raw_emails)} raw emails for today.")
        app_logger.debug(f"Raw emails fetched for today: {[e.get('id') for e in raw_emails]}")

        processed_emails = []
        email_threads = {} # Group emails by threadId

        for raw_email in raw_emails:
            email_id = raw_email.get('id', 'N/A')
            app_logger.debug(f"Processing raw email ID: {email_id}")
            try:
                processed_email = self.email_processor.parse_message(raw_email)
                processed_emails.append(processed_email)
                thread_id = processed_email['threadId']
                if thread_id not in email_threads:
                    email_threads[thread_id] = []
                    app_logger.debug(f"Created new thread: {thread_id}")
                email_threads[thread_id].append(processed_email)
                app_logger.debug(f"Email {email_id} added to thread {thread_id}.")
            except Exception as e:
                app_logger.error(f"Error processing email {email_id}: {e}", exc_info=True)
                continue
        
        app_logger.info(f"Processed {len(processed_emails)} emails. Grouped into {len(email_threads)} threads.")
        
        final_results = []
        for thread_id, emails_in_thread in email_threads.items():
            app_logger.info(f"Analyzing thread {thread_id} with {len(emails_in_thread)} emails.")
            thread_analysis = self.thread_analyzer.analyze_thread(emails_in_thread)
            app_logger.debug(f"Thread {thread_id} analysis results: Replied={thread_analysis['replied']}, Priority={thread_analysis['priority']}, DraftNeeded={thread_analysis['draft_reply_needed']}")
            
            # Get the last email in the thread for summarization and reply generation
            last_email_in_thread = emails_in_thread[-1] 
            app_logger.debug(f"Last email in thread {thread_id} for summarization/reply: {last_email_in_thread.get('id')}")

            # Summarize the entire email thread
            app_logger.info(f"Summarizing thread {thread_id}...")
            try:
                summary = await self.summarizer.summarize_email(emails_in_thread)
                last_email_in_thread['summary'] = summary
                app_logger.debug(f"Summary for thread {thread_id}: {summary[:100]}...") # Log first 100 chars of summary
            except Exception as e:
                app_logger.error(f"Error summarizing email thread {thread_id}: {e}", exc_info=True)
                last_email_in_thread['summary'] = "Error generating summary."
            
            draft_reply = "N/A"
            if Settings.ENABLE_REPLY_GENERATION and thread_analysis['draft_reply_needed']:
                app_logger.info(f"Generating reply for thread {thread_id}...")
                try:
                    # The recipient of the reply should be the sender of the last email in the thread
                    recipient_email = last_email_in_thread.get('sender', 'N/A')
                    draft_reply = await self.reply_generator.generate_reply(emails_in_thread, recipient=recipient_email)
                    app_logger.debug(f"Draft reply for thread {thread_id}: {draft_reply[:100]}...") # Log first 100 chars of reply
                except Exception as e:
                    app_logger.error(f"Error generating reply for email thread {thread_id}: {e}", exc_info=True)
                    draft_reply = "Error generating reply draft."
            else:
                app_logger.info(f"Reply generation skipped for thread {thread_id}. Enable_reply_generation: {Settings.ENABLE_REPLY_GENERATION}, Draft_reply_needed: {thread_analysis['draft_reply_needed']}")
            last_email_in_thread['draftReply'] = draft_reply # Changed to draftReply
            
            # Update the last email in thread with analysis results
            last_email_in_thread['replied'] = thread_analysis['replied']
            last_email_in_thread['priority'] = thread_analysis['priority']
            last_email_in_thread['threadId'] = thread_id # Ensure threadId is present

            # Format for export (now directly matches Pydantic model)
            # No need for data_processor.format_email_for_export if keys already match Pydantic model
            final_results.append({
                "id": last_email_in_thread.get('id', 'N/A'), # Add id field
                "sender": last_email_in_thread.get('sender', 'N/A'),
                "subject": last_email_in_thread.get('subject', 'N/A'),
                "date": last_email_in_thread.get('date', 'N/A'),
                "summary": last_email_in_thread.get('summary', 'N/A'),
                "replied": last_email_in_thread.get('replied', False),
                "draftReply": last_email_in_thread.get('draftReply', 'N/A'),
                "priority": last_email_in_thread.get('priority', 'Low'),
                "threadId": last_email_in_thread.get('threadId', 'N/A')
            })
            app_logger.debug(f"Formatted email {last_email_in_thread.get('id')} for final results. Current results count: {len(final_results)}")

        app_logger.info("Email processing complete. Returning final results.")
        return final_results

    def export_results(self, data, filename=None):
        """
        Exports the processed email data to a CSV file.
        """
        self.csv_exporter.export_to_csv(data, filename)
