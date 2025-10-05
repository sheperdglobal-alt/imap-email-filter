"""PDF Processing and OCR Module

This module handles PDF file processing, text extraction,
and OCR functionality for scanned documents.
"""

import pdfplumber
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import logging
from typing import List, Dict, Optional
import io
import os

from config import OCRConfig, AppConfig


class PDFProcessor:
    """PDF processing and OCR handler"""
    
    def __init__(self):
        """Initialize PDF processor with configuration"""
        self.logger = logging.getLogger(__name__)
        self.tesseract_path = OCRConfig.TESSERACT_PATH
        self.dpi = OCRConfig.DPI
        
        # Set tesseract path if configured
        if self.tesseract_path and os.path.exists(self.tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
    
    def extract_text_from_pdf(self, pdf_data: bytes, filename: str = "") -> Dict:
        """Extract text from PDF using multiple methods
        
        Args:
            pdf_data: PDF file as bytes
            filename: Original filename
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        result = {
            'filename': filename,
            'text': '',
            'method': 'none',
            'page_count': 0,
            'success': False
        }
        
        try:
            # First try pdfplumber (works for digital PDFs)
            text = self._extract_with_pdfplumber(pdf_data)
            
            if text and len(text.strip()) > 50:  # Threshold for meaningful text
                result['text'] = text
                result['method'] = 'pdfplumber'
                result['success'] = True
                self.logger.info(f"Extracted text from {filename} using pdfplumber")
            else:
                # Fall back to OCR for scanned documents
                self.logger.info(f"Attempting OCR for {filename}")
                text = self._extract_with_ocr(pdf_data)
                result['text'] = text
                result['method'] = 'ocr'
                result['success'] = bool(text)
                
        except Exception as e:
            self.logger.error(f"Error extracting text from {filename}: {e}")
            result['error'] = str(e)
        
        return result
    
    def _extract_with_pdfplumber(self, pdf_data: bytes) -> str:
        """Extract text using pdfplumber (for digital PDFs)
        
        Args:
            pdf_data: PDF file as bytes
            
        Returns:
            Extracted text string
        """
        text = ''
        
        with pdfplumber.open(io.BytesIO(pdf_data)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
        
        return text.strip()
    
    def _extract_with_ocr(self, pdf_data: bytes) -> str:
        """Extract text using OCR (for scanned PDFs)
        
        Args:
            pdf_data: PDF file as bytes
            
        Returns:
            Extracted text string
        """
        text = ''
        
        try:
            # Convert PDF pages to images
            images = convert_from_bytes(
                pdf_data,
                dpi=self.dpi,
                fmt=OCRConfig.IMAGE_FORMAT
            )
            
            # Perform OCR on each page
            for i, image in enumerate(images):
                self.logger.info(f"Processing page {i+1} with OCR")
                page_text = pytesseract.image_to_string(
                    image,
                    lang=OCRConfig.TESSERACT_LANG
                )
                text += page_text + '\n'
        
        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
            raise
        
        return text.strip()
    
    def extract_images_from_pdf(self, pdf_data: bytes) -> List[Image.Image]:
        """Extract images from PDF
        
        Args:
            pdf_data: PDF file as bytes
            
        Returns:
            List of PIL Image objects
        """
        images = []
        
        if not OCRConfig.EXTRACT_IMAGES:
            return images
        
        try:
            with pdfplumber.open(io.BytesIO(pdf_data)) as pdf:
                for page in pdf.pages:
                    page_images = page.images
    for img in page_images:
                        # Extract and convert image data
                        try:
                            image = Image.open(io.BytesIO(img['stream'].get_data()))
                            images.append(image)
                        except Exception as e:
                            self.logger.warning(f"Could not extract image: {e}")
        
        except Exception as e:
            self.logger.error(f"Error extracting images: {e}")
        
        return images
    
    def validate_pdf(self, pdf_data: bytes) -> bool:
        """Validate PDF file
        
        Args:
            pdf_data: PDF file as bytes
            
        Returns:
            True if valid PDF
        """
        # Check file size
        size_mb = len(pdf_data) / (1024 * 1024)
        if size_mb > OCRConfig.MAX_PDF_SIZE_MB:
            self.logger.warning(f"PDF exceeds max size: {size_mb:.2f}MB")
            return False
        
        # Check PDF signature
        if not pdf_data.startswith(b'%PDF'):
            self.logger.error("Invalid PDF signature")
            return False
        
        return True
    
    def get_pdf_metadata(self, pdf_data: bytes) -> Dict:
        """Extract PDF metadata
        
        Args:
            pdf_data: PDF file as bytes
            
        Returns:
            Dictionary containing PDF metadata
        """
        metadata = {
            'page_count': 0,
            'size_bytes': len(pdf_data),
            'size_mb': round(len(pdf_data) / (1024 * 1024), 2)
        }
        
        try:
            with pdfplumber.open(io.BytesIO(pdf_data)) as pdf:
                metadata['page_count'] = len(pdf.pages)
                
                if pdf.metadata:
                    metadata.update({
                        'title': pdf.metadata.get('Title', ''),
                        'author': pdf.metadata.get('Author', ''),
                        'subject': pdf.metadata.get('Subject', ''),
                        'creator': pdf.metadata.get('Creator', ''),
                        'producer': pdf.metadata.get('Producer', ''),
                        'creation_date': pdf.metadata.get('CreationDate', '')
                    })
        
        except Exception as e:
            self.logger.error(f"Error extracting PDF metadata: {e}")
        
        return metadata
    
    def save_text_to_file(self, text: str, output_path: str) -> bool:
        """Save extracted text to file
        
        Args:
            text: Text to save
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            self.logger.info(f"Saved extracted text to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving text to file: {e}")
            return False


if __name__ == '__main__':
    # Test the PDF processor
    logging.basicConfig(level=logging.INFO)
    
    processor = PDFProcessor()
    print("PDF Processor initialized successfully")
