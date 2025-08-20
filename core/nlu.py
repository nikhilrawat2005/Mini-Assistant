import re
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)

classifier = None

try:
    from transformers import pipeline
    classifier = pipeline("zero-shot-classification", 
                         model="facebook/bart-large-mnli")
except ImportError:
    logging.warning("Transformers not installed, using fallback NLU")

class NLU:
    def __init__(self):
        self.classifier = classifier
        
    def detect_intent(self, text: str, lang: str) -> str:
        # Reordered intents with search first
        intents = [
            'search', 'greeting', 'time', 'date', 'math',
            'conversion', 'exit', 'unknown'
        ]
        try:
            if self.classifier:
                result = self.classifier(text, intents)
                # Return the top intent
                return result['labels'][0]
        except Exception as e:
            logging.error(f"Classifier error: {e}")
        
        # Enhanced rule-based fallback
        text_lower = text.lower()
        
        # Check for search first (most common)
        search_keywords = [
            'price', 'rate', 'kya rate', 'search', 'find', 
            'dhundho', 'khojo', 'batao', 'kya bhav', 'kya daam',
            'weather', 'mausam', 'temperature', 'forecast', 'value',
            'cost', 'worth', 'bhav', 'daam', 'define', 'meaning',
            'synonyms', 'antonyms', 'translate', 'translation'
        ]
        if any(s in text_lower for s in search_keywords):
            return 'search'
        
        # Check for greetings
        if any(g in text_lower for g in ['hello', 'hi', 'namaste', 'hey', 'halo']):
            return 'greeting'
        
        # Check for time
        if 'time' in text_lower or 'samay' in text_lower or 'kitne baje' in text_lower:
            return 'time'
        
        # Check for date
        if 'date' in text_lower or 'tareekh' in text_lower or 'aaj ka din' in text_lower:
            return 'date'
        
        # Check for math
        if any(m in text_lower for m in ['calculate', 'math', 'add', 'plus', 'minus', 'multiply', 'divide', 'jod', 'ghata']):
            return 'math'
            
        # Check for exit
        if any(e in text_lower for e in ['exit', 'quit', 'bye', 'alvida', 'chalo']):
            return 'exit'
            
        return 'unknown'
    
    def extract_entities(self, text: str, lang: str) -> dict:
        """Simplified entity extraction"""
        entities = {}
        try:
            # Extract numbers
            numbers = re.findall(r'\d+', text)
            if numbers:
                entities['NUM'] = numbers[0]
                
            # Extract currency mentions
            if re.search(r'\b(price|rate|bhav|daam|cost)\b', text, re.IGNORECASE):
                entities['CURRENCY'] = 'price'
                
        except Exception as e:
            logging.error(f"Entity extraction error: {e}")
        return entities