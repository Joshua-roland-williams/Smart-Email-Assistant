from typing import List, Dict, Any
from datetime import datetime

class DataProcessor:
    """
    Utility class for formatting and processing email data.
    """
    def __init__(self):
        pass

    def format_email_for_export(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formats a single email dictionary for CSV export.
        Ensures all required columns are present.
        """
        formatted_data = {
            "Sender": email_data.get('sender', 'N/A'),
            "Subject": email_data.get('subject', 'N/A'),
            "Date": self._format_date(email_data.get('date')),
            "Email Summary": email_data.get('summary', 'N/A'),
            "Replied": "Yes" if email_data.get('replied', False) else "No",
            "Draft Reply": email_data.get('draft_reply', 'N/A'),
            "Priority": email_data.get('priority', 'Low'),
            "Thread ID": email_data.get('threadId', 'N/A')
        }
        return formatted_data

    def _format_date(self, date_str: str) -> str:
        """
        Formats a date string into a consistent YYYY-MM-DD HH:MM:SS format.
        Handles various input formats.
        """
        if not date_str:
            return "N/A"
        try:
            # Attempt to parse common date formats
            # Example: "Fri, 8 Aug 2025 03:58:49 +0530 (IST)"
            # Example: "8 Aug 2025 03:58:49 +0530"
            # Example: "2025-08-08 03:58:49"
            
            # Remove timezone info in parentheses like (IST)
            date_str = date_str.split('(')[0].strip()
            
            # Try parsing with known formats
            formats = [
                "%a, %d %b %Y %H:%M:%S %z", # Fri, 08 Aug 2025 03:58:49 +0530
                "%d %b %Y %H:%M:%S %z",    # 08 Aug 2025 03:58:49 +0530
                "%a, %d %b %Y %H:%M:%S",   # Fri, 08 Aug 2025 03:58:49 (no timezone)
                "%Y-%m-%d %H:%M:%S",      # 2025-08-08 03:58:49
                "%Y-%m-%dT%H:%M:%SZ"      # ISO format
            ]
            
            for fmt in formats:
                try:
                    dt_obj = datetime.strptime(date_str, fmt)
                    return dt_obj.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue
            
            # If no specific format matches, try a more flexible parse (might be less accurate)
            # This is a fallback and might not always work perfectly
            from dateutil import parser
            dt_obj = parser.parse(date_str)
            return dt_obj.strftime("%Y-%m-%d %H:%M:%S")

        except Exception as e:
            print(f"Error parsing date '{date_str}': {e}")
            return date_str # Return original string if parsing fails
