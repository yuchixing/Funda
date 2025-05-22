import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

def fetch_article_text(url: str) -> str | None:
    """
    Fetches HTML content from a URL and extracts meaningful text content.

    Args:
        url: The URL of the article.

    Returns:
        The extracted text as a single string, or None if an error occurs.
    """
    logger.info(f"Attempting to fetch article text from URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        article_body = None
        # Try to find common article containers more robustly
        selectors = ['article', 'main', '.post-content', '.entry-content', '.td-post-content', 'div[class*="article-content"]', 'div[class*="story-body"]']
        for selector in selectors:
            if '.' in selector or '[' in selector: # CSS selector
                 article_body = soup.select_one(selector)
            else: # Tag name
                 article_body = soup.find(selector)

            if article_body:
                logger.debug(f"Found article container with selector: {selector} for URL: {url}")
                break
        
        if not article_body:
            logger.warning(f"No specific article container found for {url}. Falling back to body.")
            article_body = soup.find('body')

        if not article_body:
            logger.error(f"Could not find body tag in {url}, which is highly unusual.")
            return None

        paragraphs = article_body.find_all('p')
        if not paragraphs:
            logger.warning(f"No <p> tags found within the identified article body for {url}. The content might be structured differently.")
            # As a fallback, try to get all text from the container, stripping extra whitespace
            text_content = article_body.get_text(separator='\n', strip=True)
        else:
            text_content = "\n".join([p.get_text(strip=True) for p in paragraphs])
        
        if text_content.strip():
            logger.info(f"Successfully extracted text content from {url} (length: {len(text_content)}).")
            return text_content.strip()
        else:
            logger.warning(f"Extracted text content is empty for {url}.")
            return None

    except requests.exceptions.Timeout:
        logger.error(f"Timeout error while fetching URL {url}.")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error {e.response.status_code} while fetching URL {url}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching URL {url}: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while parsing content from {url}: {e}", exc_info=True)
        return None

def summarize_text_with_gemini(text_content: str, api_key: str) -> str:
    """
    Summarizes the given text content using the Gemini API.

    Args:
        text_content: The text to summarize.
        api_key: The Gemini API key.

    Returns:
        The summarized text, a placeholder, or an error message.
    """
    if not text_content:
        logger.warning("Summarization skipped: No text content provided.")
        return "Summarization skipped (No text content provided)."

    # Check if the API key is None or an empty string
    if not api_key: 
        logger.warning("Summarization skipped: Gemini API key is missing or empty.")
        # Return a message consistent with how main.py might check, or a more specific one
        return "Summarization skipped (API key not configured)."


    logger.info(f"Attempting to summarize text with Gemini (text length: {len(text_content)}).")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        max_length = 100000 
        prompt = f"Please summarize the following news article text:\n\n{text_content[:max_length]}"
        if len(text_content) > max_length:
            logger.warning(f"Text content length ({len(text_content)}) exceeds max_length ({max_length}). Truncating for summarization.")

        response = model.generate_content(prompt)
        
        if response.parts:
            logger.info("Successfully generated summary with Gemini.")
            return response.text
        else:
            block_reason = "Unknown"
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                block_reason = response.prompt_feedback.block_reason
            logger.error(f"Gemini API: Content generation blocked. Reason: {block_reason}")
            return f"Gemini API: Content generation blocked. Reason: {block_reason}"

    except Exception as e:
        logger.error(f"Gemini API call failed: {e}", exc_info=True)
        return f"Gemini API call failed: {e}"

if __name__ == '__main__':
    # For direct testing of this module
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])
    
    logger.info("--- Testing summarizer.py directly ---")
    
    logger.info("--- Testing fetch_article_text ---")
    # A more robust test would involve a mock server or local HTML files.
    # Using a known public URL that is unlikely to change structure drastically for now.
    # test_url_article = "https://www.theverge.com/2023/10/26/23933449/google-ai-search-notes-search-generative-experience-labs" # Example, might be outdated
    # test_url_article = "https://example.com" # Too simple, no <p> tags often
    test_url_article = "http://example.com/nonexistent-article-for-testing" # Should fail gracefully
    
    fetched_text_test = fetch_article_text(test_url_article)
    if fetched_text_test:
        logger.info(f"Fetched text (first 200 chars): {fetched_text_test[:200]}...")
        
        logger.info("\n--- Testing summarize_text_with_gemini (with placeholder API key) ---")
        summary1_test = summarize_text_with_gemini(fetched_text_test, "YOUR_GEMINI_API_KEY")
        logger.info(f"Summary 1: {summary1_test}")

        # To test with a real API key, set it as an environment variable
        # and pass it here, e.g., os.getenv("GEMINI_API_KEY_TEST")
        # logger.info("\n--- Testing summarize_text_with_gemini (with actual API key if configured) ---")
        # import os # Make sure os is imported if using getenv here
        # actual_api_key_test = os.getenv("GEMINI_API_KEY_TEST") 
        # if actual_api_key_test:
        #     logger.info("Attempting summarization with actual API key from GEMINI_API_KEY_TEST.")
        #     summary2_test = summarize_text_with_gemini(fetched_text_test, actual_api_key_test)
        #     logger.info(f"Summary 2: {summary2_test}")
        # else:
        #     logger.info("Actual API key (GEMINI_API_KEY_TEST) not provided for this test run or is empty.")
    else:
        logger.warning(f"Could not fetch text from {test_url_article} during direct test.")

    logger.info("\n--- Testing summarize_text_with_gemini with no text ---")
    summary_no_text_test = summarize_text_with_gemini("", None) # Test with None as API key
    logger.info(f"Summary with no text (and None API key): {summary_no_text_test}")

    summary_empty_key_test = summarize_text_with_gemini("Some text", "") # Test with empty string as API key
    logger.info(f"Summary with empty string API key: {summary_empty_key_test}")
    logger.info("--- summarizer.py direct test finished ---")
