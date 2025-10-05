"""Configuration file for IMAP Email Filter with PDF OCR

This module contains all configuration settings for the IMAP email filtering
system including IMAP server settings, OCR parameters, and application settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class IMAPConfig:
    """IMAP server configuration settings"""
    
    # IMAP Server Settings
    IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.gmail.com')
    IMAP_PORT = int(os.getenv('IMAP_PORT', '993'))
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    
    # Mailbox Settings
    INBOX_FOLDER = os.getenv('INBOX_FOLDER', 'INBOX')
    PROCESSED_FOLDER = os.getenv('PROCESSED_FOLDER', 'INBOX/Processed')
    ERROR_FOLDER = os.getenv('ERROR_FOLDER', 'INBOX/Errors')
    
    # Connection Settings
    USE_SSL = os.getenv('USE_SSL', 'True').lower() == 'true'
    TIMEOUT = int(os.getenv('TIMEOUT', '30'))


class OCRConfig:
    """OCR and PDF processing configuration"""
    
    # Tesseract Settings
    TESSERACT_PATH = os.getenv('TESSERACT_PATH', '/usr/bin/tesseract')
    TESSERACT_LANG = os.getenv('TESSERACT_LANG', 'eng')
    
    # OCR Processing Settings
    DPI = int(os.getenv('OCR_DPI', '300'))
    IMAGE_FORMAT = os.getenv('IMAGE_FORMAT', 'PNG')
    
    # PDF Processing
    MAX_PDF_SIZE_MB = int(os.getenv('MAX_PDF_SIZE_MB', '50'))
    EXTRACT_IMAGES = os.getenv('EXTRACT_IMAGES', 'True').lower() == 'true'


class FilterConfig:
    """Email filtering configuration"""
    
    # Filter Settings
    FILTER_RULES_FILE = os.getenv('FILTER_RULES_FILE', 'filters/filter_rules.json')
    
    # Search Criteria
    SEARCH_UNREAD_ONLY = os.getenv('SEARCH_UNREAD_ONLY', 'True').lower() == 'true'
    SEARCH_SUBJECT_KEYWORDS = os.getenv('SEARCH_SUBJECT_KEYWORDS', 'invoice,receipt,bill').split(',')
    
    # Attachment Settings
    ALLOWED_EXTENSIONS = ['.pdf', '.PDF']
    MIN_ATTACHMENT_SIZE_KB = int(os.getenv('MIN_ATTACHMENT_SIZE_KB', '1'))


class AppConfig:
    """General application configuration"""
    
    # Directories
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'output')
    LOGS_DIR = os.getenv('LOGS_DIR', 'logs')
    TEMP_DIR = os.getenv('TEMP_DIR', 'temp')
    
    # Logging Settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.path.join(LOGS_DIR, 'email_filter.log')
    
    # Processing Settings
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', '10'))
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', '4'))
    
    # Data Storage
    SAVE_RAW_EMAILS = os.getenv('SAVE_RAW_EMAILS', 'False').lower() == 'true'
    SAVE_EXTRACTED_TEXT = os.getenv('SAVE_EXTRACTED_TEXT', 'True').lower() == 'true'
    

def validate_config():
    """Validate that all required configuration settings are present
    
    Raises:
        ValueError: If required configuration is missing or invalid
    """
    if not IMAPConfig.EMAIL_ADDRESS:
        raise ValueError("EMAIL_ADDRESS must be set in environment variables")
    
    if not IMAPConfig.EMAIL_PASSWORD:
        raise ValueError("EMAIL_PASSWORD must be set in environment variables")
    
    # Create required directories
    os.makedirs(AppConfig.OUTPUT_DIR, exist_ok=True)
    os.makedirs(AppConfig.LOGS_DIR, exist_ok=True)
    os.makedirs(AppConfig.TEMP_DIR, exist_ok=True)
    
    print("Configuration validated successfully")


if __name__ == '__main__':
    validate_config()
