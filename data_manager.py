"""Data Manager Module

Handles data storage, organization, and file management
for processed emails and extracted information.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import shutil

from config import AppConfig


class DataManager:
    """Data storage and organization manager"""
    
    def __init__(self):
        """Initialize data manager"""
        self.logger = logging.getLogger(__name__)
        self.output_dir = AppConfig.OUTPUT_DIR
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.output_dir,
            os.path.join(self.output_dir, 'pdfs'),
            os.path.join(self.output_dir, 'text'),
            os.path.join(self.output_dir, 'json'),
            os.path.join(self.output_dir, 'invoices'),
            AppConfig.LOGS_DIR,
            AppConfig.TEMP_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            self.logger.debug(f"Ensured directory exists: {directory}")
    
    def save_pdf(self, pdf_data: bytes, filename: str) -> Optional[str]:
        """Save PDF file
        
        Args:
            pdf_data: PDF file bytes
            filename: Original filename
            
        Returns:
            Saved file path or None
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = self._sanitize_filename(filename)
            output_path = os.path.join(
                self.output_dir, 
                'pdfs', 
                f"{timestamp}_{safe_filename}"
            )
            
            with open(output_path, 'wb') as f:
                f.write(pdf_data)
            
            self.logger.info(f"Saved PDF to {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Error saving PDF: {e}")
            return None
    
    def save_extracted_text(self, text: str, filename: str) -> Optional[str]:
        """Save extracted text
        
        Args:
            text: Extracted text content
            filename: Original filename
            
        Returns:
            Saved file path or None
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = self._sanitize_filename(filename)
            base_name = os.path.splitext(safe_filename)[0]
            output_path = os.path.join(
                self.output_dir,
                'text',
                f"{timestamp}_{base_name}.txt"
            )
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            self.logger.info(f"Saved extracted text to {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Error saving text: {e}")
            return None
    
    def save_invoice_data(self, invoice_data: Dict, filename: str) -> Optional[str]:
        """Save parsed invoice data as JSON
        
        Args:
            invoice_data: Parsed invoice dictionary
            filename: Original filename
            
        Returns:
            Saved file path or None
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = self._sanitize_filename(filename)
            base_name = os.path.splitext(safe_filename)[0]
            output_path = os.path.join(
                self.output_dir,
                'invoices',
                f"{timestamp}_{base_name}.json"
            )
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(invoice_data, f, indent=2, default=str)
            
            self.logger.info(f"Saved invoice data to {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Error saving invoice data: {e}")
            return None
    
    def save_email_metadata(self, metadata: Dict) -> Optional[str]:
        """Save email metadata
        
        Args:
            metadata: Email metadata dictionary
            
        Returns:
            Saved file path or None
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(
                self.output_dir,
                'json',
                f"email_metadata_{timestamp}.json"
            )
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            return output_path
        except Exception as e:
            self.logger.error(f"Error saving email metadata: {e}")
            return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove or replace unsafe characters
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        return filename[:200]  # Limit length
    
    def create_summary_report(self, processed_count: int, failed_count: int) -> Optional[str]:
        """Create a summary report of processing
        
        Args:
            processed_count: Number of successfully processed emails
            failed_count: Number of failed emails
            
        Returns:
            Report file path or None
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = os.path.join(
                self.output_dir,
                f"processing_summary_{timestamp}.txt"
            )
            
            report = f"""Email Processing Summary
            ============================
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Successfully Processed: {processed_count}
            Failed: {failed_count}
            Total: {processed_count + failed_count}
            """
            
            with open(report_path, 'w') as f:
                f.write(report)
            
            self.logger.info(f"Created summary report: {report_path}")
            return report_path
        except Exception as e:
            self.logger.error(f"Error creating summary report: {e}")
            return None
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            if os.path.exists(AppConfig.TEMP_DIR):
                for file in os.listdir(AppConfig.TEMP_DIR):
                    file_path = os.path.join(AppConfig.TEMP_DIR, file)
                    os.remove(file_path)
                self.logger.info("Cleaned up temporary files")
        except Exception as e:
            self.logger.error(f"Error cleaning up temp files: {e}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    dm = DataManager()
    print("Data Manager initialized successfully")
