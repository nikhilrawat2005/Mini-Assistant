import os
import time
from . import seed_loader, query_classifier, crawler, parser, search_index
import logging
from pathlib import Path

# Initialize logging
logger = logging.getLogger('MiniSearch')
logger.setLevel(logging.INFO)

def handle_query(user_query):
    """Main entry point for search queries"""
    try:
        # Step 1: Load Websites & Classify Query
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_dir, "seed_websites.csv")
        seed_websites = seed_loader.load_seed_websites(csv_path)
        logger.info(f"Loaded {len(seed_websites)} seed websites")
        
        category = query_classifier.classify_query(user_query, seed_websites)
        logger.info(f"Query classified as: {category}")

        # Step 2: Filter Websites for Query
        relevant_sites = [site for site in seed_websites if site['category'] == category]
        
        # Initialize database
        db_path = os.path.join(base_dir, "search_db.sqlite")
        search_index.init_db(db_path)
        
        # Step 3: Crawl & Extract Snippets
        results = []
        for site in relevant_sites[:3]:  # Limit to 3 sites for performance
            try:
                logger.info(f"Processing site: {site['website_url']}")
                html = crawler.fetch_html(site['website_url'], use_js=(site['type'] == 'JS'))
                if html:
                    text = parser.parse_html(html)
                    snippet = parser.extract_snippet(text, user_query)
                    logger.info(f"Extracted snippet: {snippet[:50]}...")
                    
                    # Store in DB
                    search_index.store_result(
                        db_path,
                        site['website_url'],
                        category,
                        snippet,
                        site['keywords']
                    )
                    results.append({
                        "url": site['website_url'],
                        "snippet": snippet,
                        "category": category
                    })
                    time.sleep(0.5)  # Reduced rate limiting
            except Exception as e:
                logger.error(f"Error processing {site['website_url']}: {str(e)}")
                continue
        
        return results if results else []
    except Exception as e:
        logger.error(f"Search engine error: {str(e)}")
        return []