"""
Sentence Processing Module
Uses NLTK for segmenting text into individual sentences.
"""

import nltk
from typing import List


def ensure_nltk_data():
    """Download required NLTK data if not present."""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab', quiet=True)


def segment_sentences(text: str) -> List[str]:
    """
    Segment text into individual sentences.
    
    Args:
        text: Input text (Spanish)
        
    Returns:
        List of sentences
    """
    ensure_nltk_data()
    
    # Use Spanish sentence tokenizer
    try:
        sentences = nltk.sent_tokenize(text, language='spanish')
    except LookupError:
        # Fallback to default if Spanish not available
        sentences = nltk.sent_tokenize(text)
    
    # Clean up sentences
    cleaned = []
    for sent in sentences:
        sent = sent.strip()
        if sent and len(sent) > 1:  # Filter out single characters
            cleaned.append(sent)
    
    return cleaned


def group_sentences_by_paragraph(text: str) -> List[List[str]]:
    """
    Split text into paragraphs, then segment each paragraph into sentences.
    
    Args:
        text: Input text with paragraph breaks
        
    Returns:
        List of paragraphs, where each paragraph is a list of sentences
    """
    ensure_nltk_data()
    
    # Split by double newlines to get paragraphs
    paragraphs = text.split('\n\n')
    
    result = []
    for para in paragraphs:
        para = para.strip()
        if para:
            sentences = segment_sentences(para)
            if sentences:
                result.append(sentences)
    
    return result
