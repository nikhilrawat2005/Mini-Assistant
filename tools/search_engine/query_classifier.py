def classify_query(query, seed_websites):
    query = query.lower()
    for site in seed_websites:
        keywords = [k.strip().lower() for k in site['keywords'].split(',')]
        if any(keyword and keyword in query for keyword in keywords):
            return site['category']
    return "General"