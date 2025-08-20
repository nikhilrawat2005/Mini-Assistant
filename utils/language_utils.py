# ---------- Simplified language_utils.py ----------
import re
from langdetect import detect, DetectorFactory
import logging

# Initialize language detector
DetectorFactory.seed = 0

def detect_language(text: str) -> str:
    """Simplified language detection without spacy"""
    if not text.strip():
        return 'en'
    
    # Check for common Hinglish words
    hinglish_words = ['ky', 'kya', 'kaise', 'thik', 'tm', 'plz', 'thoda', 
                     'chahiye', 'kr', 'kro', 'do', 'hoga', 'suno', 'batao',
                     'hal', 'hai', 'hu']
    
    if any(re.search(rf'\b{word}\b', text, re.IGNORECASE) for word in hinglish_words):
        return 'hinglish'
    
    # Standard detection
    try:
        lang = detect(text)
        if lang in ['en', 'hi']:
            return lang
        return 'en'
    except Exception:
        return 'en'

def normalize_hinglish(text: str) -> str:
    """Normalize common Hinglish terms"""
    replacements = {
        r'\bky(a|u)\b': 'kya',
        r'\bkaise\b': 'kaise',
        r'\bthik\b': 'theek',
        r'\btm\b': 'tum',
        r'\bplz\b': 'please',
        r'\bthoda\b': 'thoda',
        r'\bchahiye\b': 'chahiye',
        r'\bkr\b': 'kar',
        r'\bkro\b': 'karo',
        r'\bdo\b': 'do',
        r'\bhoga\b': 'hoga',
        r'\bsuno\b': 'suno',
        r'\bbatao\b': 'batao',
        r'\bhal\b': 'haal',
        r'\bhai\b': 'hai',
        r'\bhu\b': 'hoon'
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text