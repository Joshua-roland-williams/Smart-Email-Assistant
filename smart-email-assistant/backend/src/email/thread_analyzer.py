from datetime import datetime
import re
from ..utils.logger import logger

class ThreadAnalyzer:
    """
    Analyzes email threads to determine reply status and priority.
    """
    def __init__(self, user_email_address: str):
        self.user_email_address = user_email_address

    def analyze_thread(self, thread_emails: list):
        """
        Analyzes a list of emails within a thread to determine reply status and priority.
        Args:
            thread_emails: A list of parsed email dictionaries belonging to the same thread.
        Returns:
            A dictionary containing analysis results for the thread.
        """
        if not thread_emails:
            return {
                "replied": False,
                "priority": "Low",
                "draft_reply_needed": False,
                "last_email_from_user": False,
                "last_email_id": None
            }

        # Sort emails by date to process chronologically
        thread_emails.sort(key=lambda x: self._parse_date(x['date']))

        replied = False
        last_email_from_user = False
        last_email_id = None
        
        # Determine if the user has replied in the thread
        for email_data in thread_emails:
            if self.user_email_address in email_data['sender']:
                replied = True
                last_email_from_user = True
            else:
                last_email_from_user = False # Last email was not from user

            last_email_id = email_data['id'] # Keep track of the last email ID

        # Determine if a draft reply is needed
        # A draft reply is needed if the user has not replied AND the last email was not from the user
        draft_reply_needed = not replied and not last_email_from_user

        # Determine priority (simple heuristic for now)
        priority = self._determine_priority(thread_emails[-1]['subject'], thread_emails[-1]['body'])

        return {
            "replied": replied,
            "priority": priority,
            "draft_reply_needed": draft_reply_needed,
            "last_email_from_user": last_email_from_user,
            "last_email_id": last_email_id
        }

    def _parse_date(self, date_str: str) -> datetime:
        """Parses various date string formats into a datetime object."""
        # Example formats: "Fri, 8 Aug 2025 03:58:49 +0530 (IST)", "8 Aug 2025 03:58:49 +0530"
        try:
            # Try parsing with timezone info
            return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z (%Z)')
        except ValueError:
            try:
                return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
            except ValueError:
                try:
                    # Try parsing without timezone info, assuming local timezone
                    return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
                except ValueError:
                    try:
                        return datetime.strptime(date_str, '%d %b %Y %H:%M:%S %z')
                    except ValueError:
                        # Fallback for simpler formats or if timezone is missing/malformed
                        # This might lose timezone accuracy but ensures parsing
                        date_str_no_tz = re.sub(r'\s+\(.*\)$', '', date_str) # Remove (IST) etc.
                        date_str_no_tz = re.sub(r'(\s[+-]\d{4})', '', date_str_no_tz) # Remove +0530 etc.
                        return datetime.strptime(date_str_no_tz, '%a, %d %b %Y %H:%M:%S')
        except Exception as e:
            print(f"Could not parse date: {date_str}. Error: {e}")
            return datetime.min # Return a very old date on failure

    def _determine_priority(self, subject: str, body: str) -> str:
        """
        Determines email priority based on keywords in subject and body.
        """
        subject_lower = subject.lower()
        body_lower = body.lower()

        high_priority_keywords = ['urgent', 'action required', 'important', 'deadline', 'asap']
        medium_priority_keywords = ['follow up', 'request', 'question', 'meeting']

        if any(keyword in subject_lower for keyword in high_priority_keywords) or \
           any(keyword in body_lower for keyword in high_priority_keywords):
            return "High"
        elif any(keyword in subject_lower for keyword in medium_priority_keywords) or \
             any(keyword in body_lower for keyword in medium_priority_keywords):
            return "Medium"
        else:
            return "Low"
