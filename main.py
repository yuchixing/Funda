import logging
import time # For scheduling
import schedule # For scheduling
from feed_handler import fetch_and_parse_feed
from summarizer import fetch_article_text, summarize_text_with_gemini
from notion_writer import create_notion_page
import config # Import the new config module

# Configure logging at the very beginning
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Get a logger instance for this module
logger = logging.getLogger(__name__)

def process_news_feed_job():
    """
    Fetches, summarizes, and stores news articles based on current configuration.
    This function is intended to be scheduled.
    """
    logger.info("Job 'process_news_feed_job' starting...")

    # Use configuration variables from config.py
    logger.info(f"Fetching articles from configured RSS feed URL: {config.RSS_FEED_URL}")
    articles = fetch_and_parse_feed(url=config.RSS_FEED_URL)

    if articles:
        articles_to_process_count = min(config.MAX_ARTICLES_TO_PROCESS, len(articles))
        logger.info(f"Successfully fetched {len(articles)} articles. Attempting to process the first {articles_to_process_count}.")
        
        for i, article_item in enumerate(articles[:articles_to_process_count]): 
            article_title = article_item['title']
            article_link = article_item['link']
            logger.info(f"Processing article {i+1}/{articles_to_process_count}: \"{article_title}\" ({article_link})")
            
            article_text = fetch_article_text(article_link)
            
            if article_text:
                logger.info(f"Successfully fetched text for: {article_link} (length: {len(article_text)})")
                
                summary = "Summarization skipped (API key not configured)." # Default summary
                if not config.GEMINI_API_KEY:
                    logger.warning(f"Gemini API key not configured. Skipping summarization for \"{article_title}\".")
                else:
                    logger.info(f"Starting summarization for: {article_title}")
                    summary = summarize_text_with_gemini(article_text, config.GEMINI_API_KEY)
                    logger.info(f"Summarization finished for: {article_title}. Summary preview: {summary[:100]}...")

                # Check if summary is valid for Notion upload
                if "Summarization skipped" not in summary and \
                   "API call failed" not in summary and \
                   "No content generated" not in summary:
                    
                    if not config.NOTION_API_KEY or not config.NOTION_DATABASE_ID:
                        logger.warning(f"Notion API key or Database ID not configured. Skipping Notion page creation for \"{article_title}\".")
                    else:
                        logger.info(f"Attempting to create Notion page for: {article_title}")
                        create_notion_page(
                            api_key=config.NOTION_API_KEY,
                            database_id=config.NOTION_DATABASE_ID,
                            title=article_title,
                            summary_text=summary,
                            article_url=article_link
                        )
                else:
                    logger.warning(f"Skipping Notion page creation for \"{article_title}\" due to summarization issue or missing Notion config. Summary: {summary}")
            else:
                logger.error(f"Could not fetch article text for: {article_link}. Skipping further processing for this article.")
    else:
        logger.warning(f"No articles found from {config.RSS_FEED_URL} or an error occurred during feed parsing. Job iteration finished.")
    
    logger.info("Job 'process_news_feed_job' finished.")


if __name__ == "__main__":
    logger.info("Main application started. Setting up scheduler.")
    
    # Schedule the job
    schedule.every(config.SCHEDULE_INTERVAL_MINUTES).minutes.do(process_news_feed_job)
    logger.info(f"Scheduler configured. Job 'process_news_feed_job' will run every {config.SCHEDULE_INTERVAL_MINUTES} minutes.")

    # Run the job once immediately at startup
    logger.info("Running job 'process_news_feed_job' once at startup.")
    process_news_feed_job()
    logger.info("Initial job run completed.")

    logger.info("Starting the scheduler loop. Press Ctrl+C to exit.")
    while True:
        schedule.run_pending()
        time.sleep(1)
