"""Document processing utilities for various file formats"""
import os
import re
from pathlib import Path
from typing import List, Tuple
from abc import ABC, abstractmethod

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    from docx import Document
except ImportError:
    Document = None

from src.config.logger import setup_logger

logger = setup_logger(__name__)


class DocumentProcessor(ABC):
    """Base class for document processors"""
    
    @abstractmethod
    def process(self, file_path: str) -> str:
        """Process a document and return its text content"""
        pass


class PDFProcessor(DocumentProcessor):
    """Process PDF files"""
    
    def process(self, file_path: str) -> str:
        """Extract text from PDF"""
        if PyPDF2 is None:
            raise ImportError("PyPDF2 is required for PDF processing")
        
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    # Add proper spacing between pages
                    if page_text:
                        text += page_text + "\n\n"
            logger.info(f"Successfully processed PDF: {file_path}")
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            raise
        
        return text


class TextProcessor(DocumentProcessor):
    """Process TXT files"""
    
    def process(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            logger.info(f"Successfully processed TXT: {file_path}")
        except Exception as e:
            logger.error(f"Error processing TXT {file_path}: {str(e)}")
            raise
        
        return text


class CSVProcessor(DocumentProcessor):
    """Process CSV files"""
    
    def process(self, file_path: str) -> str:
        """Convert CSV to text"""
        if pd is None:
            raise ImportError("pandas is required for CSV processing")
        
        try:
            df = pd.read_csv(file_path)
            text = df.to_string()
            logger.info(f"Successfully processed CSV: {file_path}")
        except Exception as e:
            logger.error(f"Error processing CSV {file_path}: {str(e)}")
            raise
        
        return text


class ExcelProcessor(DocumentProcessor):
    """Process Excel files (.xlsx)"""
    
    def process(self, file_path: str) -> str:
        """Convert Excel to text"""
        if pd is None:
            raise ImportError("pandas is required for Excel processing")
        
        text = ""
        try:
            excel_file = pd.ExcelFile(file_path)
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                text += f"\n--- Sheet: {sheet_name} ---\n"
                text += df.to_string()
            logger.info(f"Successfully processed Excel: {file_path}")
        except Exception as e:
            logger.error(f"Error processing Excel {file_path}: {str(e)}")
            raise
        
        return text


class DocxProcessor(DocumentProcessor):
    """Process DOCX files"""
    
    def process(self, file_path: str) -> str:
        """Extract text from DOCX"""
        if Document is None:
            raise ImportError("python-docx is required for DOCX processing")
        
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            logger.info(f"Successfully processed DOCX: {file_path}")
        except Exception as e:
            logger.error(f"Error processing DOCX {file_path}: {str(e)}")
            raise
        
        return text


class DocumentProcessorFactory:
    """Factory for creating appropriate document processors"""
    
    _processors = {
        'pdf': PDFProcessor(),
        'txt': TextProcessor(),
        'csv': CSVProcessor(),
        'xlsx': ExcelProcessor(),
        'docx': DocxProcessor(),
    }
    
    @classmethod
    def get_processor(cls, file_extension: str) -> DocumentProcessor:
        """Get appropriate processor for file type"""
        extension = file_extension.lower().strip('.')
        if extension not in cls._processors:
            raise ValueError(f"Unsupported file type: {extension}")
        return cls._processors[extension]
    
    @classmethod
    def process_document(cls, file_path: str) -> str:
        """Process a document file and return its content"""
        file_extension = Path(file_path).suffix
        processor = cls.get_processor(file_extension)
        return processor.process(file_path)


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\-\:\;]', '', text)
    return text.strip()


def extract_metadata(file_path: str) -> dict:
    """Extract file metadata"""
    file_stat = os.stat(file_path)
    return {
        "file_name": os.path.basename(file_path),
        "file_path": file_path,
        "file_size_bytes": file_stat.st_size,
        "file_extension": Path(file_path).suffix.lower(),
        "uploaded_at": file_stat.st_mtime,
    }
