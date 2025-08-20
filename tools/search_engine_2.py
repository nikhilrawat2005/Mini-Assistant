import os
import requests
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SearchEngine2')

# --- CONFIG ---
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "75fc0191afbb48cfa6511bbc6189ccc4")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "c0d1498a293d1724cff35cd9b34d230d")

# Try to import Wikipedia with fallback
try:
    import wikipedia
    HAS_WIKIPEDIA = True
except ImportError:
    HAS_WIKIPEDIA = False
    logger.warning("Wikipedia package not installed. Using REST API fallback.")

def api_search(query: str) -> List[Dict[str, Any]]:
    query = query.lower().strip()
    results = []

    try:
        # 1. NEWS
        if "news" in query or "समाचार" in query or "खबर" in query:
            logger.info(f"Processing news query: {query}")
            url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get("articles", [])
            
            if not articles:
                return [{"snippet": "No latest news found.", "url": ""}]
            
            for article in articles[:5]:
                results.append({
                    "snippet": article.get("title", "No title"),
                    "url": article.get("url", ""),
                    "source": "NewsAPI"
                })
            
            return results

        # 2. WEATHER
        elif "weather" in query or "mausam" in query or "मौसम" in query:
            logger.info(f"Processing weather query: {query}")
            # Extract city name
            city = query.replace("dhundo", "").replace("weather", "").replace("mausam", "").strip()
            if not city:
                return [{"snippet": "Please specify a city name for weather information.", "url": ""}]
            
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get("cod") != 200:
                return [{"snippet": f"Could not fetch weather for {city}.", "url": ""}]
            
            desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            
            weather_info = f"Weather in {city.title()}: {desc}, Temperature: {temp}°C, Humidity: {humidity}%"
            return [{"snippet": weather_info, "url": "", "source": "OpenWeatherMap"}]

        # 3. WIKIPEDIA (default)
        else:
            logger.info(f"Processing Wikipedia query: {query}")
            topic = query.replace("dhundo", "").replace("search", "").strip()
            
            if not topic:
                return [{"snippet": "Please specify what to search on Wikipedia.", "url": ""}]
            
            try:
                if HAS_WIKIPEDIA:
                    # Use Wikipedia package if available
                    summary = wikipedia.summary(topic, sentences=2, auto_suggest=True, redirect=True)
                    page = wikipedia.page(topic, auto_suggest=True)
                    return [{
                        "snippet": summary,
                        "url": page.url,
                        "source": "Wikipedia"
                    }]
                else:
                    # Fallback to Wikipedia REST API
                    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic.replace(' ', '_')}"
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    
                    data = response.json()
                    summary = data.get("extract", f"Summary not available for {topic}.")
                    
                    return [{
                        "snippet": summary,
                        "url": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
                        "source": "Wikipedia"
                    }]
                    
            except Exception as e:
                logger.error(f"Wikipedia search error: {e}")
                return [{"snippet": f"Could not find information about '{topic}'.", "url": ""}]

    except requests.RequestException as e:
        logger.error(f"Network error during search: {e}")
        return [{"snippet": "Search service is currently unavailable. Please try again later.", "url": ""}]
    except Exception as e:
        logger.error(f"Unexpected error during search: {e}")
        return [{"snippet": "An unexpected error occurred during search.", "url": ""}]