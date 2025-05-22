import feedparser
import logging

logger = logging.getLogger(__name__)

def fetch_and_parse_feed(url="https://news.buzzing.cc/feed.xml"):
    """
    Fetches and parses a feed from a given URL, then extracts the title and 
    primary link for each news article.

    Args:
        url (str): The URL of the feed to fetch. Defaults to "https://news.buzzing.cc/feed.xml".

    Returns:
        list: A list of dictionaries, where each dictionary has 'title' and 'link' keys.
              Returns an empty list if no entries are found or an error occurs.
    """
    articles = []
    logger.info(f"Attempting to fetch and parse feed from URL: {url}")
    try:
        feed = feedparser.parse(url)

        if feed.bozo:
            # bozo is True if the feed is not well-formed XML
            logger.error(f"Error parsing feed from {url}. Bozo exception: {feed.bozo_exception}")
            return []

        if not feed.entries:
            logger.warning(f"No entries found in the feed from {url}")
            return []

        logger.info(f"Found {len(feed.entries)} entries in feed: {url}")
        for entry in feed.entries:
            title = getattr(entry, 'title', 'Untitled Article')
            link = getattr(entry, 'link', None)
            
            if link: # Only add entries that have a link
                articles.append({'title': title, 'link': link})
            else:
                logger.warning(f"Entry '{title}' from feed {url} has no link. Skipping.")
        
        return articles

    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching or parsing the feed from {url}: {e}", exc_info=True)
        return []

if __name__ == '__main__':
    # This block is for direct testing of this module.
    # It needs its own logging configuration if you run it directly.
    # Note: The main.py script already configures global logging.
    # For isolated testing, you might want to configure basic logging here too.
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])
    
    logger.info("--- Testing feed_handler.py directly ---")
    feed_url_test = "https://news.buzzing.cc/feed.xml"
    logger.info(f"Fetching articles from: {feed_url_test}")
    
    extracted_articles_test = fetch_and_parse_feed(feed_url_test)
    
    if extracted_articles_test:
        logger.info("Extracted Articles:")
        for article_test in extracted_articles_test:
            logger.info(f"- Title: {article_test['title']}")
            logger.info(f"  Link: {article_test['link']}")
    else:
        logger.info("No articles were extracted during the direct test.")

    logger.info("--- Testing with a known problematic feed URL (example) ---")
    problematic_feed_url_test = "http://nonexistentfeed.example.com/feed.xml"
    logger.info(f"Fetching articles from: {problematic_feed_url_test}")
    problematic_articles_test = fetch_and_parse_feed(problematic_feed_url_test)
    if not problematic_articles_test:
        logger.info("Correctly handled problematic feed URL: No articles extracted or error logged.")
    else:
        logger.error("Problematic feed URL test failed: Articles were extracted or no error was logged properly.")
    logger.info("--- feed_handler.py direct test finished ---")
