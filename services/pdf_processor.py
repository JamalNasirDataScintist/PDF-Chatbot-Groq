"""
PDF Processing Service
Extracts text from PDF documents for NLP processing
"""

import logging
from typing import Optional, Tuple
import PyPDF2

logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Handles PDF text extraction and preprocessing
    
    Uses PyPDF2 for robust PDF text extraction
    Cleans and normalizes extracted text for optimal NLP processing
    """

    def extract_text(self, pdf_path: str) -> Tuple[Optional[str], int]:
        """
        Extract text from a PDF file
        
        Args:
            pdf_path: Absolute path to the PDF file
            
        Returns:
            Tuple of (extracted_text, page_count)
            Returns (None, 0) if extraction fails
        """
        try:
            text = ""
            page_count = 0

            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                page_count = len(reader.pages)
                
                logger.info(f"Processing PDF: {page_count} page(s)")

                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n[Page {i + 1}]\n{page_text}\n"

            # Clean and normalize text
            cleaned_text = self._clean_text(text)
            
            logger.info(f"Extracted {len(cleaned_text)} characters from {page_count} pages")
            
            return cleaned_text, page_count

        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}")
            return None, 0

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text
        
        - Removes null bytes
        - Normalizes whitespace
        - Preserves paragraph structure
        """
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Normalize spaces while preserving newlines
        lines = [' '.join(line.split()) for line in text.split('\n')]
        text = '\n'.join(line for line in lines if line.strip())
        
        return text.strip()
