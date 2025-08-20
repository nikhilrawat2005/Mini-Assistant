import os
import requests
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('DictionaryTool')

class DictionaryTool:
    def __init__(self):
        self.dict_api = "https://api.dictionaryapi.dev/api/v2/entries/en/"
        self.datamuse_api = "https://api.datamuse.com/words"
        self.translate_api = "https://libretranslate.com/translate"
        self.languages_api = "https://libretranslate.com/languages"
        self.supported_languages = self._load_supported_languages()

    def _load_supported_languages(self) -> Dict[str, str]:
        """Load supported languages with caching"""
        try:
            response = requests.get(self.languages_api, timeout=5)
            if response.status_code == 200:
                return {lang['code']: lang['name'] for lang in response.json()}
            return {}
        except Exception as e:
            logger.error(f"Error loading supported languages: {e}")
            return {}

    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages for translation"""
        return self.supported_languages

    def define_word(self, word: str) -> str:
        """Fetch definitions, synonyms, antonyms, and examples for a word"""
        if not word:
            return "❌ Please provide a word to define."
            
        url = f"{self.dict_api}{word}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                return f"❌ No definition found for '{word}'."

            data = response.json()[0]
            output = [f"📖 Word: {data.get('word', word)}"]

            # Extract phonetics
            phonetics = [p.get("text") for p in data.get("phonetics", []) if p.get("text")]
            if phonetics:
                output.append(f"🔊 Pronunciation: {', '.join(phonetics)}")

            # Extract meanings
            for meaning in data.get("meanings", []):
                part = meaning.get("partOfSpeech", "")
                output.append(f"\n➡️ {part.capitalize()}:")
                
                for idx, definition in enumerate(meaning.get("definitions", []), 1):
                    def_text = definition.get("definition", "")
                    example = definition.get("example", "")
                    syns = ", ".join(definition.get("synonyms", []))
                    ants = ", ".join(definition.get("antonyms", []))
                    
                    output.append(f"   {idx}. {def_text}")
                    if example:
                        output.append(f"      Example: {example}")
                    if syns:
                        output.append(f"      Synonyms: {syns}")
                    if ants:
                        output.append(f"      Antonyms: {ants}")

            return "\n".join(output)

        except requests.RequestException:
            return "❌ Network error. Please check your connection and try again."
        except Exception as e:
            logger.error(f"Error defining word: {e}")
            return f"⚠️ Error: {str(e)}"

    def synonyms(self, word: str) -> str:
        """Fetch synonyms from Datamuse"""
        if not word:
            return "❌ Please provide a word to find synonyms for."
            
        try:
            response = requests.get(self.datamuse_api, params={"rel_syn": word}, timeout=5)
            if response.status_code == 200:
                words = [w["word"] for w in response.json()]
                if words:
                    return f"🔗 Synonyms of '{word}': " + ", ".join(words[:15])
            return f"❌ No synonyms found for '{word}'."
        except requests.RequestException:
            return "❌ Network error. Please check your connection and try again."
        except Exception as e:
            logger.error(f"Error fetching synonyms: {e}")
            return f"⚠️ Error: {str(e)}"

    def antonyms(self, word: str) -> str:
        """Fetch antonyms from Datamuse"""
        if not word:
            return "❌ Please provide a word to find antonyms for."
            
        try:
            response = requests.get(self.datamuse_api, params={"rel_ant": word}, timeout=5)
            if response.status_code == 200:
                words = [w["word"] for w in response.json()]
                if words:
                    return f"🔗 Antonyms of '{word}': " + ", ".join(words[:15])
            return f"❌ No antonyms found for '{word}'."
        except requests.RequestException:
            return "❌ Network error. Please check your connection and try again."
        except Exception as e:
            logger.error(f"Error fetching antonyms: {e}")
            return f"⚠️ Error: {str(e)}"

    def translate(self, text: str, source: str = "auto", target: str = "en") -> str:
        """Translate text using LibreTranslate"""
        if not text:
            return "❌ Please provide text to translate."
            
        try:
            # Validate target language
            if target not in self.supported_languages:
                return f"❌ Unsupported target language: {target}. Use 'list languages' to see supported languages."
                
            # Validate source language (auto is always valid)
            if source != "auto" and source not in self.supported_languages:
                return f"❌ Unsupported source language: {source}. Use 'list languages' to see supported languages."

            payload = {
                "q": text,
                "source": source,
                "target": target,
                "format": "text"
            }
            
            response = requests.post(self.translate_api, data=payload, timeout=10)
            if response.status_code == 200:
                translated_text = response.json().get('translatedText', '')
                source_lang = source if source != "auto" else "auto-detected"
                return f"🌐 Translation ({source_lang} → {target}): {translated_text}"
            
            return "❌ Translation failed. Please try again later."
            
        except requests.RequestException:
            return "❌ Network error. Please check your connection and try again."
        except Exception as e:
            logger.error(f"Error during translation: {e}")
            return f"⚠️ Error: {str(e)}"