"""
PDF Text Extraction Module
Uses PyMuPDF (fitz) to extract text from PDF files while preserving structure.
"""

import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text from a PDF file while preserving paragraph structure.
    
    Args:
        pdf_file: File-like object (from Streamlit uploader) or path to PDF
        
    Returns:
        Extracted text as a string with paragraph breaks preserved
    """
    # Read the PDF bytes
    if hasattr(pdf_file, 'read'):
        pdf_bytes = pdf_file.read()
        pdf_file.seek(0)  # Reset file pointer for potential reuse
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    else:
        doc = fitz.open(pdf_file)
    
    all_text = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Extract text blocks to preserve structure
        blocks = page.get_text("blocks")
        
        page_text = []
        for block in blocks:
            if block[6] == 0:  # Text block (not image)
                text = block[4].strip()
                if text:
                    # Clean up the text
                    text = clean_text(text)
                    page_text.append(text)
        
        if page_text:
            all_text.append("\n\n".join(page_text))
    
    doc.close()
    
    return "\n\n".join(all_text)


def clean_text(text: str) -> str:
    """
    Clean extracted text by fixing common PDF extraction artifacts.
    
    Args:
        text: Raw extracted text
        
    Returns:
        Cleaned text
    """
    # Replace multiple spaces with single space
    import re
    text = re.sub(r' +', ' ', text)
    
    # Fix hyphenation at line breaks (common in PDFs)
    text = re.sub(r'-\n', '', text)
    
    # Replace single newlines with space (preserve double newlines for paragraphs)
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    
    # Clean up multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()
