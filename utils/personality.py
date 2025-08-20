# ---------- personality.py ----------
import random

def shape_response(response: str, lang: str, context: dict) -> str:
    """Add personality and language-appropriate formatting"""
    # Hindi/Hinglish responses
    if lang in ['hi', 'hinglish']:
        starters = ["जी बिल्कुल!", "अरे वाह!", "देखिए:", 
                   "Ye lo:", "Aapke liye:", "Suniyo:"]
        enders = ["\n\nऔर जानकारी चाहिए?", "\nकुछ और?", 
                 "\n\nAur chahiye?", "\nKuch aur poocho?"]
    
    # English responses
    else:
        starters = ["Sure thing!", "Here you go:", "Check this out:",
                   "Interesting!", "I found this:"]
        enders = ["\n\nNeed more details?", "\nAnything else?", 
                 "\n\nWant me to dig deeper?"]
    
    # Add personality based on context
    if 'last_bot' in context and context['last_bot']:
        starter = random.choice(starters[1:])  # Avoid repetition
    else:
        starter = starters[0]
    
    # Format response
    return f"{starter} {response}{random.choice(enders)}"