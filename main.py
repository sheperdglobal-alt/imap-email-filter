#!/usr/bin/env python3
"""Main Application Entry Point

IMAP Email Filter with PDF OCR - Main application that coordinates
email fetching, PDF processing, OCR, and data extraction.
"""

import logging
import sys
from typing import List, Dict

from config import IMAPConfig, AppConfig, validate_config
from email_client import EmailClient
from pdf_processor import PDFProcessor
from invoice_parser import InvoiceParser
from data_manager import DataManager


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, AppConfig.LOG_LEVEL),
        format=AppConfig.LOG_FORMAT,
        handlers=[
            logging.FileHandler(AppConfig.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )


class EmailFilterApp:
    """Main application class"""
    
    def __init__(self):
        """Initialize the application"""
        self.logger = logging.getLogger(__name__)
        self.email_client = EmailClient()
        self.pdf_processor = PDFProcessor()
        self.invoice_parser = InvoiceParser()
        self.data_manager = DataManager()
        
        self.processed_count = 0
        self.failed_count = 0
    
    def run(self):
        """Main application run method"""
        self.logger.info("Starting IMAP Email Filter Application")
        
        try:
            # Connect to email server
            if not self.email_client.connect():
                self.logger.error("Failed to connect to email server")
                return False
            
            # Select inbox
            if not self.email_client.select_folder():
                self.logger.error("Failed to select inbox folder")
                return False
            
            # Get unread emails
            email_ids = self.email_client.get_unread_emails()
            self.logger.info(f"Found {len(email_ids)} unread emails")
            
            if not email_ids:
                self.logger.info("No unread emails to process")
                return True
            
            # Process each email
            for email_id in email_ids:
                self.process_email(email_id)
            
            # Create summary report
            self.data_manager.create_summary_report(
                self.processed_count,
                self.failed_count
            )
            
            self.logger.info(f"Processed: {self.processed_count}, Failed: {self.failed_count}")
            return True
            
        except Exception as e:
            self.logger.error(f"Application error: {e}", exc_info=True)
            return False
        
        finally:
            self.email_client.disconnect()
            self.data_manager.cleanup_temp_files()
    
    def process_email(self, email_id: bytes):
        """Process a single email
        
        Args:
            email_id: Email ID to process
        """
        try:
            self.logger.info(f"Processing email {email_id.decode()}")
            
            # Fetch email
            email_msg = self.email_client.fetch_email(email_id)
            if not email_msg:
                self.logger.warning(f"Could not fetch email {email_id}")
                self.failed_count += 1
                return
            
            # Get email metadata
            metadata = self.email_client.get_email_metadata(email_msg)
            self.logger.info(f"Processing email from: {metadata['from']}")
            self.logger.info(f"Subject: {metadata['subject']}")
            
            # Get attachments
            attachments = self.email_client.get_attachments(email_msg)
            
            if not attachments:
                self.logger.info(f"No PDF attachments found in email {email_id}")
                self.email_client.mark_as_read(email_id)
                return
            
            # Process each attachment
            for attachment in attachments:
                self.process_attachment(attachment, metadata)
            
            # Mark email as read
            self.email_client.mark_as_read(email_id)
            self.processed_count += 1
            
        except Exception as e:
            self.logger.error(f"Error processing email {email_id}: {e}")
            self.failed_count += 1
    
    def process_attachment(self, attachment: Dict, email_metadata: Dict):
        """Process a PDF attachment
        
        Args:
            attachment: Attachment dictionary
            email_metadata: Email metadata dictionary
        """
        try:
            filename = attachment['filename']
            pdf_data = attachment['payload']
            
            self.logger.info(f"Processing attachment: {filename}")
            
            # Validate PDF
            if not self.pdf_processor.validate_pdf(pdf_data):
                self.logger.warning(f"Invalid PDF: {filename}")
                return
            
            # Save original PDF
            if AppConfig.SAVE_RAW_EMAILS:
                self.data_manager.save_pdf(pdf_data, filename)
            
            # Extract text from PDF
            extraction_result = self.pdf_processor.extract_text_from_pdf(
                pdf_data,
                filename
            )
            
            if not extraction_result['success']:
                self.logger.warning(f"Text extraction failed for {filename}")
                return
            
            extracted_text = extraction_result['text']
            
            # Save extracted text
            if AppConfig.SAVE_EXTRACTED_TEXT:
                self.data_manager.save_extracted_text(extracted_text, filename)
            
            # Parse invoice data
            invoice_data = self.invoice_parser.parse_invoice(extracted_text)
            
            # Add metadata
            invoice_data['email_metadata'] = email_metadata
            invoice_data['filename'] = filename
            invoice_data['extraction_method'] = extraction_result['method']
            
            # Validate and save invoice data
            if self.invoice_parser.validate_invoice_data(invoice_data):
                self.data_manager.save_invoice_data(invoice_data, filename)
                self.logger.info(f"Successfully processed invoice: {invoice_data.get('invoice_number', 'N/A')}")
            else:
                self.logger.warning(f"Invoice validation failed for {filename}")
            
        except Exception as e:
            self.logger.error(f"Error processing attachment {filename}: {e}")


def main():
    """Main entry point"""
    print("="*50)
    print("IMAP Email Filter with PDF OCR")
    print("="*50)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Validate configuration
        validate_config()
        
        # Create and run application
        app = EmailFilterApp()
        success = app.run()
        
        if success:
            print("\nApplication completed successfully!")
            return 0
        else:
            print("\nApplication encountered errors.")
            return 1
            
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nFatal error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
