"""
File extraction service for parsing uploaded documents.
Supports .txt, .pdf, and .docx files.
"""

import io
from pathlib import Path
from pypdf import PdfReader
from docx import Document


def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """
    Extract text content from an uploaded file.

    Args:
        file_content: Raw bytes of the uploaded file
        filename: Original filename (used to determine file type)

    Returns:
        Extracted text content

    Raises:
        ValueError: If file type is not supported
    """
    suffix = Path(filename).suffix.lower()

    if suffix == '.txt':
        return extract_from_txt(file_content)
    elif suffix == '.pdf':
        return extract_from_pdf(file_content)
    elif suffix in ['.docx', '.doc']:
        return extract_from_docx(file_content)
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Supported types: .txt, .pdf, .docx")


def extract_from_txt(content: bytes) -> str:
    """Extract text from a plain text file."""
    # Try common encodings
    for encoding in ['utf-8', 'utf-16', 'latin-1', 'cp1252']:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    # Fallback with error handling
    return content.decode('utf-8', errors='replace')


def extract_from_pdf(content: bytes) -> str:
    """Extract text from a PDF file."""
    reader = PdfReader(io.BytesIO(content))
    text_parts = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)

    return '\n\n'.join(text_parts)


def extract_from_docx(content: bytes) -> str:
    """Extract text from a Word document."""
    doc = Document(io.BytesIO(content))
    text_parts = []

    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text_parts.append(paragraph.text)

    return '\n\n'.join(text_parts)


# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# Supported extensions
SUPPORTED_EXTENSIONS = {'.txt', '.pdf', '.docx', '.doc'}
