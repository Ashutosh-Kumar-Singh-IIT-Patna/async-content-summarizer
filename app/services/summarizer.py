from openai import OpenAI
from app.config import Config
from app.utils.helpers import generic_retry
import logging

logger = logging.getLogger(__name__)

# Initialize LLM client
client = OpenAI(
    base_url=Config.LLM_ENDPOINT,
    api_key=Config.LLM_TOKEN,
)


@generic_retry()
def summarize(text: str) -> str:
    """Generate a summary of the provided text using LLM"""
    logger.info("Starting summarization for text of length: %d", len(text))

    try:
        response = client.chat.completions.create(
            model=Config.LLM_MODEL,
            messages=[
                {"role": "system", "content": "Summarize the following text"},
                {"role": "user", "content": text},
            ],
            timeout=20,
        )

        content = response.choices[0].message.content
        summary = content.strip() if content else ""
        logger.info(
            "Summarization completed successfully, summary length: %d", len(summary)
        )

        return summary

    except Exception as e:
        logger.error("Summarization failed: %s", str(e))
        raise
