import csv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SeedLoader')

def load_seed_websites(csv_path):
    websites = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if not all(key in row for key in ['category', 'website_url', 'type', 'keywords']):
                    logger.warning(f"Skipping malformed row: {row}")
                    continue
                websites.append(row)
        logger.info(f"Successfully loaded {len(websites)} websites")
    except Exception as e:
        logger.error(f"Failed to load seed websites: {e}")
    return websites