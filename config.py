import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# API Keys and Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Application Settings
RSS_FEED_URL = os.getenv("RSS_FEED_URL", "https://news.buzzing.cc/feed.xml")
# Ensure SCHEDULE_INTERVAL_MINUTES is an int, default to 10 if not set or invalid
try:
    SCHEDULE_INTERVAL_MINUTES = int(os.getenv("SCHEDULE_INTERVAL_MINUTES", "10"))
except ValueError:
    SCHEDULE_INTERVAL_MINUTES = 10

# Ensure MAX_ARTICLES_TO_PROCESS is an int, default to 3 if not set or invalid
try:
    MAX_ARTICLES_TO_PROCESS = int(os.getenv("MAX_ARTICLES_TO_PROCESS", "3"))
except ValueError:
    MAX_ARTICLES_TO_PROCESS = 3

if __name__ == '__main__':
    # For testing purposes, print the loaded variables
    print(f"GEMINI_API_KEY: {GEMINI_API_KEY}")
    print(f"NOTION_API_KEY: {NOTION_API_KEY}")
    print(f"NOTION_DATABASE_ID: {NOTION_DATABASE_ID}")
    print(f"RSS_FEED_URL: {RSS_FEED_URL}")
    print(f"SCHEDULE_INTERVAL_MINUTES: {SCHEDULE_INTERVAL_MINUTES}")
    print(f"MAX_ARTICLES_TO_PROCESS: {MAX_ARTICLES_TO_PROCESS}")
