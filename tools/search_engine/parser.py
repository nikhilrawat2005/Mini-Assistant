from bs4 import BeautifulSoup
import re

def parse_html(html):
    try:
        soup = BeautifulSoup(html, 'lxml')
    except Exception:
        soup = BeautifulSoup(html, 'html.parser')
    
    for script in soup(["script", "style", "nav", "footer", "noscript"]):
        script.decompose()
    
    text = soup.get_text(separator=' ', strip=True)
    text = re.sub(r'\s+', ' ', text)
    return text


def extract_snippet(text, query, max_length=300):
    query_words = [w.lower() for w in re.findall(r'\w+', query)]
    if not query_words:
        return text[:max_length]
    
    # Find best window with most query words
    words = text.split()
    best_score = 0
    best_start = 0
    
    for i in range(len(words)):
        window = ' '.join(words[i:i+20]).lower()
        score = sum(1 for w in query_words if w in window)
        if score > best_score:
            best_score = score
            best_start = i
    
    snippet = ' '.join(words[best_start:best_start+20])
    snippet = snippet[:max_length]
    
    # Highlight query words
    for word in query_words:
        snippet = re.sub(f'({word})', r'**\1**', snippet, flags=re.IGNORECASE)
    
    return snippet + ('...' if len(snippet) >= max_length else '')