import requests
from bs4 import BeautifulSoup
from app.utils.helpers import generic_retry
import logging

logger = logging.getLogger(__name__)

# Limit content length to avoid excessive data
MAX_CONTENT_LENGTH = 10000


@generic_retry()
def fetch_url_content(url: str) -> str:
    """Fetch and extract text content from a URL"""
    logger.info("Fetching content from URL: %s", url)

    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        logger.info(
            "Successfully fetched content from URL: %s, status: %d",
            url,
            resp.status_code,
        )

        # Parse HTML and extract text
        soup = BeautifulSoup(resp.content, "html.parser")
        content = soup.get_text(separator="\n", strip=True)

        # Truncate content to max length
        truncated_content = content[:MAX_CONTENT_LENGTH]
        logger.info(
            "Extracted content length: %d (truncated to %d)",
            len(content),
            len(truncated_content),
        )

        return truncated_content

    except requests.RequestException as e:
        logger.error("Failed to fetch content from URL %s: %s", url, str(e))
        raise
    except Exception as e:
        logger.error("Unexpected error processing content from URL %s: %s", url, str(e))
        raise
