# tools/offline_tools.py
import math
import os
import platform
import random
import time
import threading
import requests
from datetime import datetime
from typing import Optional, List, Dict
import ast
import re

# ---------------- SECURITY HELPER ----------------
def sanitize_path(user_path: str) -> str:
    """Prevent path traversal attacks"""
    base_dir = os.path.abspath(os.getcwd())
    resolved_path = os.path.abspath(os.path.join(base_dir, user_path))
    
    if not resolved_path.startswith(base_dir):
        raise ValueError("Path traversal attempt detected")
    
    return resolved_path

# ---------------- SAFE MATH EVALUATION (FIXED) ----------------
def safe_eval(expr: str) -> float:
    """Evaluate math expressions safely with trigonometric support"""
    tree = ast.parse(expr, mode='eval')
    
    # Whitelist of allowed functions and constants
    allowed_names = {
        'pi': math.pi, 
        'e': math.e,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'sqrt': math.sqrt
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Only allow calls to whitelisted functions
            if not isinstance(node.func, ast.Name) or node.func.id not in allowed_names:
                raise ValueError("Function calls not allowed")
        if isinstance(node, (ast.Attribute, ast.Subscript)):
            raise ValueError("Attribute access not allowed")
        if isinstance(node, ast.Name) and node.id not in allowed_names:
            raise ValueError(f"Invalid identifier: {node.id}")
    
    return eval(compile(tree, '<string>', 'eval'), {'__builtins__': None}, allowed_names)

# ---------------- DATE & TIME ----------------
def current_time() -> str:
    return datetime.now().strftime("Current time: %H:%M:%S")

def current_date() -> str:
    return datetime.now().strftime("Today: %A, %d %B %Y")

def day_of_week() -> str:
    return datetime.now().strftime("%A")

# ---------------- MATH ----------------
def simple_math(expr: str) -> Optional[str]:
    try:
        result = safe_eval(expr)
        return f"Result: {result}"
    except Exception as e:
        return f"Could not calculate: {e}"

# ---------------- FILE OPERATIONS ----------------
def read_file(file_path: str) -> str:
    try:
        safe_path = sanitize_path(file_path)
        if os.path.exists(safe_path):
            with open(safe_path, "r", encoding="utf-8") as f:
                return f.read()
        return "File not found."
    except Exception as e:
        return f"Error: {e}"

def write_file(file_path: str, content: str) -> str:
    try:
        safe_path = sanitize_path(file_path)
        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Written to {safe_path}."
    except Exception as e:
        return f"Error: {e}"

def append_file(file_path: str, content: str) -> str:
    try:
        safe_path = sanitize_path(file_path)
        with open(safe_path, "a", encoding="utf-8") as f:
            f.write(content + "\n")
        return f"Appended to {safe_path}."
    except Exception as e:
        return f"Error: {e}"

def file_stats(file_path: str) -> str:
    try:
        safe_path = sanitize_path(file_path)
        if os.path.exists(safe_path):
            with open(safe_path, "r", encoding="utf-8") as f:
                text = f.read()
            lines = len(text.splitlines())
            words = len(text.split())
            chars = len(text)
            return f"Lines: {lines}, Words: {words}, Characters: {chars}"
        return "File not found."
    except Exception as e:
        return f"Error: {e}"

def search_in_file(file_path: str, keyword: str) -> str:
    try:
        safe_path = sanitize_path(file_path)
        if os.path.exists(safe_path):
            with open(safe_path, "r", encoding="utf-8") as f:
                matches = [line.strip() for line in f if keyword.lower() in line.lower()]
            if matches:
                return f"Found lines:\n" + "\n".join(matches)
            return f"No matches for '{keyword}'"
        return "File not found."
    except Exception as e:
        return f"Error: {e}"

# ---------------- RANDOM / FUN ----------------
def random_number(start=0, end=100) -> str:
    return f"Random number: {random.randint(start, end)}"

def random_choice(items: List[str]) -> str:
    if items:
        return f"Random choice: {random.choice(items)}"
    return "No items provided."

def coin_toss() -> str:
    return random.choice(["Heads", "Tails"])

def dice_roll() -> str:
    return f"Dice rolled: {random.randint(1, 6)}"

# ---------------- TEXT UTILITIES ----------------
def word_count(text: str) -> str:
    return f"Words: {len(text.split())}, Characters: {len(text)}"

def reverse_text(text: str) -> str:
    return text[::-1]

def capitalize_text(text: str) -> str:
    return text.upper()

def search_and_replace(text: str, search: str, replace: str) -> str:
    return text.replace(search, replace)

# ---------------- REMINDERS / TIMER ----------------
def set_timer(seconds: int, message: str):
    def notify():
        print(f"[TIMER] {message}")
    threading.Timer(seconds, notify).start()
    return f"Timer set for {seconds} seconds."

# ---------------- UNIT CONVERSION ----------------
def convert_length(value: float, from_unit: str, to_unit: str) -> float:
    mapping = {"cm": 1, "inch": 2.54}
    if from_unit.lower() in mapping and to_unit.lower() in mapping:
        return value * mapping[from_unit.lower()] / mapping[to_unit.lower()]
    return None

def convert_weight(value: float, from_unit: str, to_unit: str) -> float:
    mapping = {"kg": 1, "lb": 0.453592}
    if from_unit.lower() in mapping and to_unit.lower() in mapping:
        return value * mapping[from_unit.lower()] / mapping[to_unit.lower()]
    return None

def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    if from_unit.lower() == "c" and to_unit.lower() == "f":
        return value * 9/5 + 32
    elif from_unit.lower() == "f" and to_unit.lower() == "c":
        return (value - 32) * 5/9
    return None

# ---------------- NOTES / TODO ----------------
NOTES_FILE = os.path.join(os.path.dirname(__file__), "notes.txt")

def add_note(note: str) -> str:
    return append_file(NOTES_FILE, note)

def read_notes() -> str:
    return read_file(NOTES_FILE)

def delete_notes() -> str:
    try:
        safe_path = sanitize_path(NOTES_FILE)
        if os.path.exists(safe_path):
            os.remove(safe_path)
            return "All notes deleted."
        return "No notes found."
    except Exception as e:
        return f"Error: {e}"

# ---------------- JOKES & FACTS (MIXED ONLINE/OFFLINE) ----------------
LOCAL_JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "What did one ocean say to the other ocean? Nothing, they just waved!",
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "Why don't skeletons fight each other? They don't have the guts!",
    "What do you call a fake noodle? An impasta!"
]

LOCAL_FACTS = [
    "Honey never spoils.",
    "Bananas are berries, but strawberries aren't.",
    "Octopuses have three hearts.",
    "The Eiffel Tower can be 15 cm taller during hot days.",
    "A day on Venus is longer than a year on Venus."
]

def get_online_joke():
    """Fetch a joke from online API with fallback to local jokes"""
    try:
        # Try JokeAPI first
        response = requests.get("https://v2.jokeapi.dev/joke/Any?safe-mode", timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data['type'] == 'single':
                return data['joke']
            else:
                return f"{data['setup']} ... {data['delivery']}"
        
        # Fallback to icanhazdadjoke
        response = requests.get("https://icanhazdadjoke.com/", 
                               headers={"Accept": "text/plain"}, 
                               timeout=2)
        if response.status_code == 200:
            return response.text
            
    except (requests.RequestException, KeyError):
        pass
    
    # If all online attempts fail, use local jokes
    return random.choice(LOCAL_JOKES)

def get_online_fact():
    """Fetch a fact from online API with fallback to local facts"""
    try:
        # Try uselessfacts API
        response = requests.get("https://uselessfacts.jsph.pl/random.json?language=en", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return data['text']
            
        # Fallback to api-ninjas
        response = requests.get("https://api.api-ninjas.com/v1/facts", 
                               headers={"X-Api-Key": "YOUR_API_KEY"}, 
                               timeout=2)
        if response.status_code == 200 and response.json():
            return response.json()[0]['fact']
            
    except (requests.RequestException, KeyError):
        pass
    
    # If all online attempts fail, use local facts
    return random.choice(LOCAL_FACTS)

def random_joke() -> str:
    """Get a random joke (online with offline fallback)"""
    return get_online_joke()

def random_fact() -> str:
    """Get a random fact (online with offline fallback)"""
    return get_online_fact()

# ---------------- MINI SELF-AWARENESS (SIMPLIFIED HELP) ----------------
def mini_help() -> str:
    """Return simplified help information"""
    return """
I'm Mini! Just say the keyword + your request.  

📖 DICTIONARY:
  • define <word> → word definition
  • synonyms <word> → synonyms
  • antonyms <word> → antonyms
  • translate <text> to <lang> → translate text

🔍 SEARCH:
  • dhundo <query> → search the web
  • dhundo weather <city> → weather information
  • dhundo news → latest news

🕒 DATE & TIME:
  • time → current time
  • date → today's date
  • day → day of the week

📝 NOTES:
  • addnote [text] → save note
  • readnotes → show notes
  • deletenotes → clear all notes

⏰ REMINDERS:
  • timer [seconds] [message] → set timer

🧮 MATH:
  • math [expression] → calculate
  • calculate [expression] → calculate

📏 CONVERSIONS:
  • convertlength [value] [from] [to]
  • convertweight [value] [from] [to]
  • converttemp [value] [from] [to]

🎲 FUN:
  • random → random number
  • choice [items] → random choice
  • coin → coin toss
  • dice → dice roll
  • fact → random fact

🔤 TEXT:
  • count [text] → word count
  • reverse [text] → reverse text
  • capitalize [text] → uppercase text
  • replace [text] [search] [replace]

📁 FILES:
  • read [file] → read file
  • write [file] [text] → write file
  • append [file] [text] → append to file
  • stats [file] → file statistics
  • searchfile [file] [keyword] → search in file

❓ HELP:
  • help → show this list
  • about → info about Mini
"""

def about_mini() -> str:
    """Information about Mini"""
    return ("I'm Mini, your personal assistant! " 
            "I can answer questions, perform calculations, manage files, "
            "set timers, convert units, translate text, and much more. "
            "Just ask me anything or say 'help' for available commands.")

# ---------------- COMMAND MAPPING ----------------
COMMAND_MAPPINGS = {
    "time": lambda _: current_time(),
    "date": lambda _: current_date(),
    "day": lambda _: day_of_week(),
    "math": simple_math,
    "read": read_file,
    "write": write_file,
    "append": append_file,
    "stats": file_stats,
    "searchfile": search_in_file,
    "random": lambda args: random_number(*map(int, args.split())) if args else random_number(),
    "choice": lambda args: random_choice(args.split(',')),
    "coin": lambda _: coin_toss(),
    "dice": lambda _: dice_roll(),
    "fact": lambda _: random_fact(),
    "count": word_count,
    "reverse": reverse_text,
    "capitalize": capitalize_text,
    "replace": lambda args: search_and_replace(*args.split(' ', 2)),
    "timer": lambda args: set_timer(int(args.split()[0]), ' '.join(args.split()[1:])) if args else "Please specify time and message",
    "convertlength": lambda args: f"{convert_length(*map(float, args.split()[:2]), args.split()[2])}" if len(args.split()) >= 3 else "Invalid format",
    "convertweight": lambda args: f"{convert_weight(*map(float, args.split()[:2]), args.split()[2])}" if len(args.split()) >= 3 else "Invalid format",
    "converttemp": lambda args: f"{convert_temperature(*map(float, args.split()[:2]), args.split()[2])}" if len(args.split()) >= 3 else "Invalid format",
    "addnote": add_note,
    "readnotes": read_notes,
    "deletenotes": delete_notes,
    "help": lambda _: mini_help(),
    "about": lambda _: about_mini()
}

# ---------------- NATURAL QUERY HANDLER (EXPANDED) ----------------
def handle_natural_query(query: str) -> Optional[str]:
    """Handle natural language queries using keyword + free-form matching"""
    query_lower = query.lower().strip()

    # ---------------- HELP / ABOUT ----------------
    if any(k in query_lower for k in ['help', 'commands', 'madad', 'sahayata']):
        return mini_help()
    if any(k in query_lower for k in ['about', 'baare', 'jaankaari']):
        return about_mini()

    # ---------------- DATE / TIME ----------------
    if any(k in query_lower for k in ['time', 'samay', 'baje', 'kitne baje', 'vaqt']):
        return current_time()
    if any(k in query_lower for k in ['date', 'tareekh', 'aaj ki taareekh', 'dinank']):
        return current_date()
    if any(k in query_lower for k in ['day', 'din', 'aaj kaun sa din', 'vaar']):
        return f"Today is {day_of_week()}"

    # ---------------- NOTES ----------------
    note_match = re.search(r'\b(note|likho|likh do|yaad rakhna)\b(.*)', query_lower)
    if note_match:
        note_text = note_match.group(2).strip()
        if note_text:
            return add_note(note_text)
        return "What note should I save?"

    if any(k in query_lower for k in ['read notes', 'notes dekho', 'notes padho']):
        return read_notes()
    if any(k in query_lower for k in ['delete notes', 'notes delete', 'notes hatao']):
        return delete_notes()

    # ---------------- REMINDERS ----------------
    reminder_match = re.search(
        r'(?:reminder|remind me|yaad dilana|alarm)\s*(\d{1,2}):(\d{2})\s*(am|pm)?\s*\(?([^)]*)\)?', 
        query_lower
    )
    if reminder_match:
        hour = int(reminder_match.group(1))
        minute = int(reminder_match.group(2))
        ampm = reminder_match.group(3)
        message = reminder_match.group(4).strip() or "Reminder!"

        if ampm == "pm" and hour < 12:
            hour += 12
        if ampm == "am" and hour == 12:
            hour = 0

        now = datetime.now()
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target < now:
            target = target.replace(day=now.day + 1)  # push to next day if already passed

        seconds = max(1, int((target - now).total_seconds()))
        set_timer(seconds, message)
        return f"Reminder set for {target.strftime('%I:%M %p')} with message: {message}"

    # ---------------- MATH ----------------
    if any(k in query_lower for k in ['sum', 'add', '+', 'jod', 'jama']):
        nums = [int(n) for n in re.findall(r'\d+', query_lower)]
        if len(nums) >= 2:
            return f"Result: {sum(nums)}"
    if any(k in query_lower for k in ['subtract', 'minus', '-', 'ghatao', 'ghatana']):
        nums = [int(n) for n in re.findall(r'\d+', query_lower)]
        if len(nums) >= 2:
            return f"Result: {nums[0] - nums[1]}"
    if any(k in query_lower for k in ['multiply', 'product', '*', 'guna', 'gunana']):
        nums = [int(n) for n in re.findall(r'\d+', query_lower)]
        if len(nums) >= 2:
            result = 1
            for n in nums: 
                result *= n
            return f"Result: {result}"
    if any(k in query_lower for k in ['divide', '/', 'bhaag', 'vibhajit']):
        nums = [int(n) for n in re.findall(r'\d+', query_lower)]
        if len(nums) >= 2:
            if nums[1] == 0:
                return "Cannot divide by zero"
            return f"Result: {nums[0] / nums[1]:.2f}"

    # ---------------- CONVERSIONS ----------------
    conversion_match = re.search(r'convert\s+(\d+(?:\.\d+)?)\s+(\w+)\s+to\s+(\w+)', query_lower)
    if conversion_match:
        value = float(conversion_match.group(1))
        from_unit = conversion_match.group(2)
        to_unit = conversion_match.group(3)

        # Length conversion
        if from_unit in ['cm', 'inch'] and to_unit in ['cm', 'inch']:
            result = convert_length(value, from_unit, to_unit)
            return f"{value} {from_unit} = {result:.2f} {to_unit}"
        # Weight conversion
        if from_unit in ['kg', 'lb'] and to_unit in ['kg', 'lb']:
            result = convert_weight(value, from_unit, to_unit)
            return f"{value} {from_unit} = {result:.2f} {to_unit}"
        # Temperature conversion
        if from_unit in ['c', 'f'] and to_unit in ['c', 'f']:
            result = convert_temperature(value, from_unit, to_unit)
            return f"{value}°{from_unit.upper()} = {result:.1f}°{to_unit.upper()}"

    # ---------------- RANDOM / FUN ----------------
    if any(k in query_lower for k in ['random number', 'any number', 'random sankhya']):
        return random_number()
    if any(k in query_lower for k in ['random choice', 'choose', 'chun lo']):
        items = re.findall(r'\b\w+\b', query_lower.split('choice', 1)[-1])
        return random_choice(items)
    if any(k in query_lour for k in ['coin', 'toss', 'sikka uthao']):
        return coin_toss()
    if any(k in query_lower for k in ['dice', 'roll', 'dice pheko']):
        return dice_roll()
    if any(k in query_lower for k in ['fact', 'tathya', 'rochak jankari']):
        return random_fact()

    # ---------------- TEXT UTILITIES ----------------
    if any(k in query_lower for k in ['word count', 'count words', 'shabd ginti']):
        return word_count(query)
    if any(k in query_lower for k in ['reverse', 'ulta', 'palt do']):
        return reverse_text(query.split('reverse', 1)[-1].strip())
    if any(k in query_lower for k in ['capitalize', 'uppercase', 'bade akshar']):
        return capitalize_text(query.split('capitalize', 1)[-1].strip())
    if any(k in query_lower for k in ['replace', 'badlo', 'replace karo']):
        parts = query.split()
        if len(parts) >= 4:
            return search_and_replace(' '.join(parts[1:]), parts[1], parts[2])

    # ---------------- FILE OPS ----------------
    if any(k in query_lower for k in ['read file', 'file padho', 'file read']):
        match = re.search(r'read file (.+)', query_lower)
        if match:
            return read_file(match.group(1))
    if any(k in query_lower for k in ['write file', 'file likho', 'file write']):
        parts = query.split("write file", 1)[-1].strip().split(" ", 1)
        if len(parts) == 2:
            return write_file(parts[0], parts[1])
    if any(k in query_lower for k in ['append file', 'file append', 'file jodo']):
        parts = query.split("append file", 1)[-1].strip().split(" ", 1)
        if len(parts) == 2:
            return append_file(parts[0], parts[1])

    # ---------------- FALLBACK ----------------
    return None