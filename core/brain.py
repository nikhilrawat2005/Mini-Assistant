import os
import json
import re
import random
import requests
import logging
from datetime import datetime
from typing import Optional
from utils.language_utils import detect_language, normalize_hinglish
from utils.personality import shape_response
from core.nlu import NLU
from tools import offline_tools
from tools.search_engine_2 import api_search
from tools.dictionary import DictionaryTool

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Brain')

# Optional func_timeout import
try:
    from func_timeout import func_timeout, FunctionTimedOut
    HAS_FUNC_TIMEOUT = True
except ImportError:
    HAS_FUNC_TIMEOUT = False
    class FunctionTimedOut(Exception): pass

class Brain:
    def __init__(self, memory_path: Optional[str] = None):
        self.memory_path = memory_path or "data/memory.json"
        self.context = {
            "last_user": "",
            "last_bot": "",
            "pending_action": None,
            "language": "en"
        }
        self.memory = self.load_memory()
        self.nlu = NLU()
        self.dictionary = DictionaryTool()
        
        # Initialize search engines
        self.search_engine = api_search
        
        # Direct command mappings (word -> function)
        self.command_mappings = {
            # Date & Time
            "time": offline_tools.current_time,
            "date": offline_tools.current_date,
            "day": offline_tools.day_of_week,
            
            # Math
            "math": offline_tools.simple_math,
            "calculate": offline_tools.simple_math,
            
            # File Operations
            "read": offline_tools.read_file,
            "write": offline_tools.write_file,
            "append": offline_tools.append_file,
            "stats": offline_tools.file_stats,
            "searchfile": offline_tools.search_in_file,
            
            # Random & Fun
            "random": offline_tools.random_number,
            "choice": offline_tools.random_choice,
            "coin": offline_tools.coin_toss,
            "dice": offline_tools.dice_roll,
            "fact": offline_tools.random_fact,
            
            # Text Utilities
            "count": offline_tools.word_count,
            "reverse": offline_tools.reverse_text,
            "capitalize": offline_tools.capitalize_text,
            "replace": offline_tools.search_and_replace,
            
            # Timer
            "timer": offline_tools.set_timer,
            
            # Unit Conversion
            "convertlength": lambda args: offline_tools.convert_length(*args.split()),
            "convertweight": lambda args: offline_tools.convert_weight(*args.split()),
            "converttemp": lambda args: offline_tools.convert_temperature(*args.split()),
            
            # Notes
            "addnote": offline_tools.add_note,
            "readnotes": offline_tools.read_notes,
            "deletenotes": offline_tools.delete_notes,
            
            # Dictionary
            "define": self.handle_define,
            "synonyms": self.handle_synonyms,
            "antonyms": self.handle_antonyms,
            "translate": self.handle_translate,
            
            # Help
            "help": offline_tools.mini_help,
            "about": offline_tools.about_mini,
            
            # Special commands
            "dhundo": self.handle_dhundo_command
        }
        
    def load_memory(self):
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading memory: {e}")
                return {"conversations": [], "facts": {}, "stats": {}}
        return {"conversations": [], "facts": {}, "stats": {}}
    
    def save_memory(self):
        try:
            os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    def touch_stat(self, stat_name: str):
        """Increment a statistic counter in memory"""
        if "stats" not in self.memory:
            self.memory["stats"] = {}
        self.memory["stats"][stat_name] = self.memory["stats"].get(stat_name, 0) + 1
        self.save_memory()
    
    def handle_direct_command(self, command: str, args: str) -> Optional[str]:
        """Handle direct commands using the command mapping"""
        if command in self.command_mappings:
            try:
                func = self.command_mappings[command]
                if callable(func):
                    if args:
                        return func(args)  # function with arguments
                    return func()        # function without arguments
                return "Command not implemented properly"
            except Exception as e:
                logger.error(f"Error executing command '{command}': {e}")
                return f"Error executing command: {e}"
        return None
        
    def handle_dhundo_command(self, args: str) -> str:
        """Handle 'dhundo' command using search_engine_2"""
        if not args:
            return "Please specify what to search after 'dhundo'"
        self.touch_stat('api_search')
        try:
            return self.search_engine(args)
        except Exception as e:
            logger.error(f"API search error: {e}")
            return "Search service is currently unavailable"
    
    def handle_define(self, args: str) -> str:
        """Handle word definition requests"""
        if not args:
            return "Please specify a word to define"
        self.touch_stat('dictionary_lookups')
        try:
            return self.dictionary.define_word(args)
        except Exception as e:
            logger.error(f"Dictionary error: {e}")
            return "Dictionary service is currently unavailable"
    
    def handle_synonyms(self, args: str) -> str:
        """Handle synonym requests"""
        if not args:
            return "Please specify a word to find synonyms for"
        self.touch_stat('synonym_requests')
        try:
            return self.dictionary.synonyms(args)
        except Exception as e:
            logger.error(f"Synonym error: {e}")
            return "Could not fetch synonyms at this time"
    
    def handle_antonyms(self, args: str) -> str:
        """Handle antonym requests"""
        if not args:
            return "Please specify a word to find antonyms for"
        self.touch_stat('antonym_requests')
        try:
            return self.dictionary.antonyms(args)
        except Exception as e:
            logger.error(f"Antonym error: {e}")
            return "Could not fetch antonyms at this time"
    
    def handle_translate(self, args: str) -> str:
        """Handle translation requests with flexible syntax"""
        if not args:
            return "Please specify text to translate. Format: translate <text> to <lang>"
        
        self.touch_stat('translation_requests')
        
        # Handle different translation syntax patterns
        patterns = [
            r'(.+?)\s+to\s+(\w+)$',  # "text to lang"
            r'from\s+(\w+)\s+to\s+(\w+)\s+(.+)$',  # "from src to tgt text"
            r'(\w+)\s+(.+)$',  # "lang text"
        ]
        
        source_lang = "auto"
        target_lang = "en"
        text = args
        
        for pattern in patterns:
            match = re.search(pattern, args, re.IGNORECASE)
            if match:
                if pattern == patterns[0]:  # "text to lang"
                    text, target_lang = match.groups()
                elif pattern == patterns[1]:  # "from src to tgt text"
                    source_lang, target_lang, text = match.groups()
                elif pattern == patterns[2]:  # "lang text"
                    target_lang, text = match.groups()
                break
        
        try:
            return self.dictionary.translate(text.strip(), source=source_lang, target=target_lang)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return "Translation service is currently unavailable"
        
    def process(self, user_text: str) -> str:
        # Detect language
        lang = detect_language(user_text)
        self.context['language'] = lang
        logger.info(f"Language detected: {lang}")
        
        # Normalize Hinglish
        original_text = user_text
        if lang == 'hinglish':
            user_text = normalize_hinglish(user_text)
            logger.info(f"Normalized Hinglish: {user_text}")
        
        # Create lowercase version for intent detection
        user_text_lower = user_text.lower()
        
        # Try to handle as direct command
        parts = user_text.strip().split(maxsplit=1)
        if parts:
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            direct_response = self.handle_direct_command(command, args)
            if direct_response:
                return direct_response
        
        # Try natural language handler for direct commands
        natural_response = offline_tools.handle_natural_query(user_text)
        if natural_response:
            return natural_response
        
        # Intent recognition
        intent = self.nlu.detect_intent(user_text, lang)
        logger.info(f"Detected intent: {intent} for text: {user_text}")
        
        # Update context
        self.context['last_user'] = user_text
        
        # ---------------- INTENT HANDLING ----------------
        if intent == 'greeting':
            self.touch_stat('greetings')
            greetings = {
                'en': ["Hello!", "Hi there!", "Hey!"],
                'hi': ["नमस्ते!", "प्रणाम!", "हैलो!"],
                'hinglish': ["Hi ji!", "Kaise ho?", "Sab badhiya?"]
            }
            return random.choice(greetings[lang])
        
        elif intent == 'time':
            self.touch_stat('time_queries')
            current_time = datetime.now().strftime("%H:%M")
            responses = {
                'en': f"The current time is {current_time}",
                'hi': f"समय है {current_time}",
                'hinglish': f"Time abhi hai {current_time}"
            }
            return shape_response(responses[lang], lang, self.context)
        
        elif intent == 'date':
            self.touch_stat('date_queries')
            current_date = datetime.now().strftime("%A, %d %B %Y")
            responses = {
                'en': f"Today is {current_date}",
                'hi': f"आज की तारीख है {current_date} ",
                'hinglish': f"Aaj ki date hai {current_date}"
            }
            return shape_response(responses[lang], lang, self.context)
        
        elif intent == 'math':
            self.touch_stat('math_queries')
            try:
                expr = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', user_text)
                if expr:
                    num1, operator, num2 = int(expr.group(1)), expr.group(2), int(expr.group(3))
                    
                    if operator == '+': result = num1 + num2
                    elif operator == '-': result = num1 - num2
                    elif operator == '*': result = num1 * num2
                    elif operator == '/':
                        if num2 == 0:
                            self.touch_stat('math_errors')
                            return "Cannot divide by zero"
                        result = num1 / num2
                    
                    self.touch_stat('math_success')
                    return f"{num1} {operator} {num2} = {result}"
                
                self.touch_stat('math_errors')
                return "Please provide a simple math expression like '2+2'"
            except Exception as e:
                logger.error(f"Math error: {e}")
                self.touch_stat('math_errors')
                return "Could not calculate"
        
        elif intent == 'search':
            self.touch_stat('search_requests')
            clean_query = re.sub(r'\b(mini|search|find)\b', '', user_text, flags=re.IGNORECASE).strip()
            logger.info(f"Processing search query: '{clean_query}' (Original: '{original_text}')")
            
            try:
                # USE NEW SEARCH ENGINE HERE
                if HAS_FUNC_TIMEOUT:
                    results = func_timeout(10, self.search_engine, args=(clean_query,))
                else:
                    results = self.search_engine(clean_query)
                
                if results:
                    # Format results with URLs and snippets
                    formatted_results = []
                    for res in results[:3]:  # Show top 3 results
                        if res.get('snippet'):
                            formatted_results.append(
                                f"🔗 {res.get('url', 'No URL')}\n"
                                f"{res['snippet']}\n"
                            )
                    
                    if formatted_results:
                        self.touch_stat('search_success')
                        response = "Here's what I found:\n\n" + "\n".join(formatted_results)
                        return shape_response(response, lang, self.context)
                    
                self.touch_stat('search_empty')
                return "No relevant results found. Try different keywords."
                
            except FunctionTimedOut:
                self.touch_stat('search_timeout')
                return "Search took too long. Please try again with more specific terms."
            except Exception as e:
                logger.error(f"Search failed: {e}")
                self.touch_stat('search_errors')
                return "Search service is currently unavailable. Please try again later."
        
        # ---------------- FALLBACK ----------------
        self.touch_stat('fallback_responses')
        fallbacks = {
            'en': "I'm still learning, could you rephrase?",
            'hi': "मैं अभी सीख रहा हूँ, क्या आप दोबारा कह सकते हैं?",
            'hinglish': "Mein abhi seekh raha hoon, phirse bolo?"
        }
        return fallbacks[lang]
    
    def store_data_from_links(self, links: list, folder_name: str) -> str:
        """
        Stores data from provided links into a folder inside 'data/'.
        If folder exists, use it. Otherwise, create it.
        Each link's data is stored as a separate JSON file with a sanitized filename.
        """
        base_path = "data"
        target_path = os.path.join(base_path, folder_name)
        
        # Ensure target folder exists
        os.makedirs(target_path, exist_ok=True)
        
        saved_files = []
        
        for idx, url in enumerate(links, start=1):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    content = response.text
                    
                    # Generate safe filename
                    filename = f"link_{idx}.json"
                    file_path = os.path.join(target_path, filename)
                    
                    # Save content as JSON
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump({
                            "url": url,
                            "content": content
                        }, f, indent=2, ensure_ascii=False)
                    
                    saved_files.append(filename)
                else:
                    logger.warning(f"Failed to fetch URL {url}: Status {response.status_code}")
            except Exception as e:
                logger.error(f"Error fetching URL {url}: {e}")
        
        if saved_files:
            return f"Data stored in folder '{folder_name}': {', '.join(saved_files)}"
        else:
            return "No data was stored, all URLs failed."