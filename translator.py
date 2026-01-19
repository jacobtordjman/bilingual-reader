"""
Local Translation Engine
Uses Helsinki-NLP/opus-mt-es-en (MarianMT) for Spanish to English translation.
Runs entirely locally on CPU/GPU without paid APIs.
"""

from typing import List, Optional
from transformers import MarianMTModel, MarianTokenizer
import torch


class Translator:
    """Local Spanish to English translator using MarianMT."""
    
    MODEL_NAME = "Helsinki-NLP/opus-mt-es-en"
    
    def __init__(self):
        self.model: Optional[MarianMTModel] = None
        self.tokenizer: Optional[MarianTokenizer] = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
    
    def load_model(self):
        """Load the translation model (downloads on first use)."""
        if self.model is None:
            self.tokenizer = MarianTokenizer.from_pretrained(self.MODEL_NAME)
            self.model = MarianMTModel.from_pretrained(self.MODEL_NAME)
            self.model.to(self.device)
            self.model.eval()
    
    def translate(self, text: str) -> str:
        """
        Translate a single text from Spanish to English.
        
        Args:
            text: Spanish text to translate
            
        Returns:
            English translation
        """
        self.load_model()
        
        # Tokenize
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate translation
        with torch.no_grad():
            translated = self.model.generate(**inputs)
        
        # Decode
        result = self.tokenizer.decode(translated[0], skip_special_tokens=True)
        return result
    
    def translate_batch(self, texts: List[str], batch_size: int = 8) -> List[str]:
        """
        Translate multiple texts in batches for efficiency.
        
        Args:
            texts: List of Spanish texts to translate
            batch_size: Number of texts to process at once
            
        Returns:
            List of English translations
        """
        self.load_model()
        
        translations = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Tokenize batch
            inputs = self.tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate translations
            with torch.no_grad():
                translated = self.model.generate(**inputs)
            
            # Decode batch
            for trans in translated:
                result = self.tokenizer.decode(trans, skip_special_tokens=True)
                translations.append(result)
        
        return translations


# Global translator instance (singleton pattern for efficiency)
_translator: Optional[Translator] = None


def get_translator() -> Translator:
    """Get the global translator instance."""
    global _translator
    if _translator is None:
        _translator = Translator()
    return _translator


def translate_spanish_to_english(text: str) -> str:
    """
    Convenience function to translate Spanish to English.
    
    Args:
        text: Spanish text
        
    Returns:
        English translation
    """
    translator = get_translator()
    return translator.translate(text)


def translate_sentences(sentences: List[str]) -> List[str]:
    """
    Translate a list of Spanish sentences to English.
    
    Args:
        sentences: List of Spanish sentences
        
    Returns:
        List of English translations (same order)
    """
    translator = get_translator()
    return translator.translate_batch(sentences)
