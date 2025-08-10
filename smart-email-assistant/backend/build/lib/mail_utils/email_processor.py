import base64
import email
from bs4 import BeautifulSoup
from datetime import datetime

class EmailProcessor:
    """
    Parses raw email data fetched from Gmail API.
    """
    def __init__(self):
        pass

    def parse_message(self, msg):
        """
        Parses a raw Gmail message object into a structured dictionary.
        """
        headers = {header['name']: header['value'] for header in msg['payload']['headers']}
        
        email_data = {
            'id': msg['id'],
            'threadId': msg['threadId'],
            'snippet': msg.get('snippet', ''),
            'sender': self._get_header_value(headers, 'From'),
            'subject': self._get_header_value(headers, 'Subject'),
            'date': self._get_header_value(headers, 'Date'),
            'body': self._get_email_body(msg['payload']),
            'is_read': 'UNREAD' not in msg['labelIds'],
            'labels': msg['labelIds']
        }
        return email_data

    def _get_header_value(self, headers, name):
        """Helper to get a header value by name."""
        return headers.get(name, 'N/A')

    def _get_email_body(self, payload):
        """
        Extracts the email body from the message payload, handling different MIME types.
        Prioritizes plain text, then HTML.
        """
        if 'parts' in payload:
            for part in payload['parts']:
                mime_type = part.get('mimeType')
                if mime_type == 'text/plain':
                    return self._decode_body_data(part.get('body', {}).get('data', ''))
                elif mime_type == 'text/html':
                    html_body = self._decode_body_data(part.get('body', {}).get('data', ''))
                    return self._html_to_plain_text(html_body)
                elif 'parts' in part: # Handle nested parts
                    nested_body = self._get_email_body(part)
                    if nested_body:
                        return nested_body
        elif 'body' in payload and 'data' in payload['body']:
            return self._decode_body_data(payload['body']['data'])
        return ""

    def _decode_body_data(self, data):
        """Decodes base64 web-safe encoded data."""
        if not data:
            return ""
        try:
            decoded_bytes = base64.urlsafe_b64decode(data)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Error decoding email body: {e}")
            return ""

    def _html_to_plain_text(self, html_content):
        """Converts HTML content to plain text using BeautifulSoup."""
        if not html_content:
            return ""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text(separator='\n')
        except Exception as e:
            print(f"Error converting HTML to plain text: {e}")
            return html_content # Return original HTML if conversion fails
