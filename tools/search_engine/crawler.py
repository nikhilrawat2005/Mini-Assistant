import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import logging
import os
from pathlib import Path

logger = logging.getLogger('Crawler')

def _driver_service():
    """Locate ChromeDriver with platform-specific paths"""
    base = Path(__file__).resolve().parent.parent
    platform_paths = {
        'win': base / "chromedriver-win64" / "chromedriver.exe",
        'linux': base / "chromedriver-linux64" / "chromedriver",
        'mac': base / "chromedriver-mac-x64" / "chromedriver"
    }
    
    for path in platform_paths.values():
        if path.exists():
            return Service(str(path))
    return None  # Fallback to Selenium Manager

def fetch_html(url, use_js=False, timeout=15):
    try:
        if not use_js:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.text
        else:
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--window-size=1280,800")
            
            service = _driver_service()
            if service:
                driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                driver = webdriver.Chrome(options=chrome_options)
                
            driver.set_page_load_timeout(timeout)
            driver.get(url)
            time.sleep(2.5)  # Wait for JS execution
            html = driver.page_source
            driver.quit()
            return html
    except Exception as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        return None