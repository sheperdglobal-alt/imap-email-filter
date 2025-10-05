"""Invoice Parser Module

This module handles parsing and extracting structured data
from invoice documents using pattern matching and regex.
"""

import re
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json


class InvoiceParser:
    """Invoice data extraction and parsing"""
    
    def __init__(self):
        """Initialize invoice parser"""
        self.logger = logging.getLogger(__name__)
    
    def parse_invoice(self, text: str) -> Dict:
        """Parse invoice data from text
        
        Args:
            text: Extracted text from invoice
            
        Returns:
            Dictionary containing parsed invoice data
        """
        invoice_data = {
            'invoice_number': self.extract_invoice_number(text),
            'date': self.extract_date(text),
            'total_amount': self.extract_total_amount(text),
            'vendor': self.extract_vendor(text),
            'items': self.extract_line_items(text),
            'tax_amount': self.extract_tax(text),
            'currency': self.extract_currency(text)
        }
        
        self.logger.info(f"Parsed invoice: {invoice_data['invoice_number']}")
        return invoice_data
    
    def extract_invoice_number(self, text: str) -> Optional[str]:
        """Extract invoice number from text
        
        Args:
            text: Invoice text
            
        Returns:
            Invoice number or None
        """
        patterns = [
            r'invoice\s*#?\s*:?\s*([A-Z0-9\-]+)',
            r'inv\s*#?\s*:?\s*([A-Z0-9\-]+)',
            r'invoice\s*number\s*:?\s*([A-Z0-9\-]+)',
            r'#\s*([A-Z0-9\-]{5,})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def extract_date(self, text: str) -> Optional[str]:
        """Extract invoice date from text
        
        Args:
            text: Invoice text
            
        Returns:
            Date string or None
        """
        patterns = [
            r'date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'invoice\s*date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def extract_total_amount(self, text: str) -> Optional[float]:
        """Extract total amount from text
        
        Args:
            text: Invoice text
            
        Returns:
            Total amount as float or None
        """
        patterns = [
            r'total\s*:?\s*\$?([0-9,]+\.\d{2})',
            r'amount\s*due\s*:?\s*\$?([0-9,]+\.\d{2})',
            r'grand\s*total\s*:?\s*\$?([0-9,]+\.\d{2})',
            r'balance\s*due\s*:?\s*\$?([0-9,]+\.\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None
    
    def extract_vendor(self, text: str) -> Optional[str]:
        """Extract vendor name from text
        
        Args:
            text: Invoice text
            
        Returns:
            Vendor name or None
        """
        patterns = [
            r'from\s*:?\s*([A-Za-z0-9\s&.,]+)(?:\n|\r)',
            r'vendor\s*:?\s*([A-Za-z0-9\s&.,]+)(?:\n|\r)',
            r'billed\s*by\s*:?\s*([A-Za-z0-9\s&.,]+)(?:\n|\r)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback: Try to get first line if it looks like a company name
        first_line = text.split('\n')[0].strip()
        if len(first_line) > 3 and len(first_line) < 100:
            return first_line
        
        return None
    
    def extract_line_items(self, text: str) -> List[Dict]:
        """Extract line items from invoice
        
        Args:
            text: Invoice text
            
        Returns:
            List of line item dictionaries
        """
        items = []
        
        # Pattern for line items (simplified)
        pattern = r'([A-Za-z0-9\s\-]+)\s+(\d+)\s+\$?([0-9,]+\.\d{2})'
        
        matches = re.finditer(pattern, text)
        for match in matches:
            items.append({
                'description': match.group(1).strip(),
                'quantity': int(match.group(2)),
                'amount': float(match.group(3).replace(',', ''))
            })
        
        return items
    
    def extract_tax(self, text: str) -> Optional[float]:
        """Extract tax amount from text
        
        Args:
            text: Invoice text
            
        Returns:
            Tax amount as float or None
        """
        patterns = [
            r'tax\s*:?\s*\$?([0-9,]+\.\d{2})',
            r'vat\s*:?\s*\$?([0-9,]+\.\d{2})',
            r'sales\s*tax\s*:?\s*\$?([0-9,]+\.\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None
    
    def extract_currency(self, text: str) -> str:
        """Extract currency from text
        
        Args:
            text: Invoice text
            
        Returns:
            Currency code (defaults to 'USD')
        """
        currencies = ['USD', 'EUR', 'GBP', 'CAD', 'AUD']
        
        for currency in currencies:
            if currency in text.upper():
                return currency
        
        # Check for currency symbols
        if '$' in text:
            return 'USD'
        elif '€' in text:
            return 'EUR'
        elif '£' in text:
            return 'GBP'
        
        return 'USD'  # Default
    
    def validate_invoice_data(self, invoice_data: Dict) -> bool:
        """Validate extracted invoice data
        
        Args:
            invoice_data: Parsed invoice dictionary
            
        Returns:
            True if data appears valid
        """
        required_fields = ['invoice_number', 'total_amount']
        
        for field in required_fields:
            if not invoice_data.get(field):
                self.logger.warning(f"Missing required field: {field}")
                return False
        
        return True
    
    def save_invoice_json(self, invoice_data: Dict, filepath: str) -> bool:
        """Save invoice data as JSON
        
        Args:
            invoice_data: Parsed invoice dictionary
            filepath: Output file path
            
        Returns:
            True if successful
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(invoice_data, f, indent=2, default=str)
            self.logger.info(f"Saved invoice data to {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving invoice JSON: {e}")
            return False


if __name__ == '__main__':
    # Test the invoice parser
    logging.basicConfig(level=logging.INFO)
    
    parser = InvoiceParser()
    print("Invoice Parser initialized successfully")
