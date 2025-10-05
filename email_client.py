"""IMAP Email Client Module

This module handles IMAP email server connections, email fetching,
and mailbox operations for the email filtering system.
"""

import imaplib
import email
from email.header import decode_header
import logging
from typing import List, Dict, Tuple, Optional
import time

from config import IMAPConfig, FilterConfig


class EmailClient:
    """IMAP email client for connecting and fetching emails"""
    
    def __init__(self):
        """Initialize the email client with configuration settings"""
        self.server = IMAPConfig.IMAP_SERVER
        self.port = IMAPConfig.IMAP_PORT
        self.email_address = IMAPConfig.EMAIL_ADDRESS
        self.password = IMAPConfig.EMAIL_PASSWORD
        self.connection = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """Connect to the IMAP server
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if IMAPConfig.USE_SSL:
                self.connection = imaplib.IMAP4_SSL(
                    self.server, 
                    self.port,
                    timeout=IMAPConfig.TIMEOUT
                )
            else:
                self.connection = imaplib.IMAP4(
                    self.server, 
                    self.port,
                    timeout=IMAPConfig.TIMEOUT
                )
            
            # Login to the server
            self.connection.login(self.email_address, self.password)
            self.logger.info(f"Successfully connected to {self.server}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to IMAP server: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the IMAP server"""
        try:
            if self.connection:
                self.connection.close()
                self.connection.logout()
                self.logger.info("Disconnected from IMAP server")
        except Exception as e:
            self.logger.error(f"Error disconnecting: {e}")
    
    def select_folder(self, folder: str = None) -> bool:
        """Select a mailbox folder
        
        Args:
            folder: Folder name (defaults to INBOX)
            
        Returns:
            bool: True if folder selected successfully
        """
        if folder is None:
            folder = IMAPConfig.INBOX_FOLDER
            
        try:
            status, messages = self.connection.select(folder)
            if status == 'OK':
                self.logger.info(f"Selected folder: {folder}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error selecting folder {folder}: {e}")
            return False
    
    def search_emails(self, criteria: str = 'ALL') -> List[bytes]:
        """Search for emails matching criteria
        
        Args:
            criteria: IMAP search criteria
            
        Returns:
            List of email IDs
        """
        try:
            status, messages = self.connection.search(None, criteria)
            if status == 'OK':
                email_ids = messages[0].split()
                self.logger.info(f"Found {len(email_ids)} emails matching criteria")
                return email_ids
            return []
        except Exception as e:
            self.logger.error(f"Error searching emails: {e}")
            return []
    
    def fetch_email(self, email_id: bytes) -> Optional[email.message.Message]:
        """Fetch a single email by ID
        
        Args:
            email_id: The email ID to fetch
            
        Returns:
            Email message object or None
        """
        try:
            status, msg_data = self.connection.fetch(email_id, '(RFC822)')
            if status == 'OK':
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                return email_message
            return None
        except Exception as e:
            self.logger.error(f"Error fetching email {email_id}: {e}")
            return None
    
    def get_email_metadata(self, msg: email.message.Message) -> Dict:
        """Extract metadata from an email message
        
        Args:
            msg: Email message object
            
        Returns:
            Dictionary containing email metadata
        """
        metadata = {
            'subject': self._decode_header(msg.get('Subject', '')),
            'from': self._decode_header(msg.get('From', '')),
            'to': self._decode_header(msg.get('To', '')),
            'date': msg.get('Date', ''),
            'message_id': msg.get('Message-ID', ''),
        }
        return metadata
    
    def _decode_header(self, header: str) -> str:
        """Decode email header
        
        Args:
            header: Email header string
            
        Returns:
            Decoded header string
        """
        if not header:
            return ''
        
        decoded_parts = decode_header(header)
        decoded_string = ''
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                try:
                    decoded_string += part.decode(encoding or 'utf-8')
                except:
                    decoded_string += part.decode('utf-8', errors='ignore')
            else:
                decoded_string += str(part)
        
        return decoded_string
    
    def get_attachments(self, msg: email.message.Message) -> List[Dict]:
        """Extract attachments from an email message
        
        Args:
            msg: Email message object
            
        Returns:
            List of attachment dictionaries with filename and payload
        """
        attachments = []
        
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            
            filename = part.get_filename()
            if filename:
                # Check if file extension is allowed
                if any(filename.endswith(ext) for ext in FilterConfig.ALLOWED_EXTENSIONS):
                    attachments.append({
                        'filename': self._decode_header(filename),
                        'payload': part.get_payload(decode=True),
                        'content_type': part.get_content_type()
                    })
        
        self.logger.info(f"Found {len(attachments)} attachments")
        return attachments
    
    def move_email(self, email_id: bytes, destination_folder: str) -> bool:
        """Move an email to a different folder
        
        Args:
            email_id: Email ID to move
            destination_folder: Destination folder name
            
        Returns:
            bool: True if successful
        """
        try:
            # Copy to destination
            result = self.connection.copy(email_id, destination_folder)
            if result[0] == 'OK':
                # Mark as deleted in current folder
                self.connection.store(email_id, '+FLAGS', '\\Deleted')
                self.connection.expunge()
                self.logger.info(f"Moved email {email_id} to {destination_folder}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error moving email: {e}")
            return False
    
    def mark_as_read(self, email_id: bytes) -> bool:
        """Mark an email as read
        
        Args:
            email_id: Email ID to mark
            
        Returns:
            bool: True if successful
        """
        try:
            self.connection.store(email_id, '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            self.logger.error(f"Error marking email as read: {e}")
            return False
    
    def get_unread_emails(self) -> List[bytes]:
        """Get all unread emails in current folder
        
        Returns:
            List of unread email IDs
        """
        return self.search_emails('UNSEEN')
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


if __name__ == '__main__':
    # Test the email client
    logging.basicConfig(level=logging.INFO)
    
    with EmailClient() as client:
        if client.select_folder():
            emails = client.get_unread_emails()
            print(f"Found {len(emails)} unread emails")
