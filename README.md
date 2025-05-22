# RSS Feed Summarizer to Notion

This project periodically fetches news articles from an RSS feed, summarizes their content using the Gemini API, and stores these summaries in a Notion database.

## Features

*   Fetches articles from a configurable RSS feed.
*   Extracts main content from article web pages.
*   Summarizes article content using Google's Gemini API.
*   Stores article title, original URL, and summary into a specified Notion database.
*   Scheduled execution to periodically check for new articles.
*   Configurable via environment variables or a `.env` file.
*   Comprehensive logging to console and `app.log` file.

## Prerequisites

*   Python 3.7+
*   Access to Google Gemini API (and an API Key)
*   Access to Notion API (and an API Key and Database ID)

## Setup Instructions

1.  **Clone the Repository (if applicable)**
    ```bash
    # git clone <repository_url>
    # cd <repository_name>
    ```

2.  **Create and Activate a Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**

    Create a `.env` file in the root of the project directory by copying the `.env.example` file:
    ```bash
    cp .env.example .env
    ```
    Then, edit the `.env` file with your actual credentials and preferences:

    *   `GEMINI_API_KEY`: Your Google Gemini API key.
    *   `NOTION_API_KEY`: Your Notion API integration token (secret).
    *   `NOTION_DATABASE_ID`: The ID of the Notion database where summaries will be stored.
    *   `RSS_FEED_URL`: (Optional) The URL of the RSS feed to monitor. Defaults to `https://news.buzzing.cc/feed.xml`.
    *   `SCHEDULE_INTERVAL_MINUTES`: (Optional) How often (in minutes) to check the feed. Defaults to `10`.
    *   `MAX_ARTICLES_TO_PROCESS`: (Optional) Maximum number of articles to process each time the job runs. Defaults to `3`.

    **Getting Notion API Key and Database ID:**
    *   **Notion API Key (Integration Token):**
        1.  Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations).
        2.  Click "New integration".
        3.  Give it a name (e.g., "RSS Summarizer").
        4.  Select the workspace where your target database resides.
        5.  Ensure "Content Capabilities" include "Read content", "Update content", and "Insert content".
        6.  Click "Submit".
        7.  Copy the "Internal Integration Token" - this is your `NOTION_API_KEY`.
    *   **Notion Database ID:**
        1.  Open the Notion database you want to use in your browser.
        2.  Share the database with the integration you just created (click "..." on the database, then "Add connections", and find your integration by its name).
        3.  The Database ID is part of the URL. For a URL like `https://www.notion.so/your-workspace/abcdef1234567890abcdef1234567890?v=...`, the Database ID is `abcdef1234567890abcdef1234567890`. It's the part between your workspace name and the `?v=`.
        4.  Ensure your database has at least these columns with the specified types:
            *   `Title` (Property type: `Title`)
            *   `Summary` (Property type: `Rich Text`)
            *   `URL` (Property type: `URL`)

## Running the Script

Once the setup is complete, run the main script from the project's root directory:

```bash
python main.py
```

The script will run the processing job once immediately and then continue running, checking the feed at the configured schedule interval.

## Project Structure

*   `main.py`: The main entry point for the application. Handles scheduling and orchestrates the workflow.
*   `config.py`: Manages configuration loading from environment variables and `.env` file.
*   `feed_handler.py`: Responsible for fetching and parsing the RSS feed.
*   `summarizer.py`: Handles fetching article content from web pages and generating summaries using the Gemini API.
*   `notion_writer.py`: Responsible for writing data (article title, summary, URL) to the Notion database.
*   `requirements.txt`: Lists all Python dependencies.
*   `.env.example`: Example file for environment variable configuration.
*   `app.log`: Log file where execution details and errors are recorded.

## Viewing Logs

Logs are printed to the console and also saved to `app.log` in the project's root directory. This file will contain timestamped information about the script's operations, including fetched articles, summarization attempts, Notion updates, and any errors encountered.
```
