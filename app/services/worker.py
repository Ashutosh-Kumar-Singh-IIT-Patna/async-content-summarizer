from celery import Celery
from dotenv import load_dotenv

load_dotenv()

from app.config import Config
from app.models import Job, JobStatus, ContentType
from app.services.content_fetcher import fetch_url_content
from app.services.summarizer import summarize
from app.services.cache_service import set_cached_summary, get_cached_summary
from app.utils.helpers import commit_pgdb
import logging
import time

logger = logging.getLogger(__name__)

celery = Celery(
    "worker",
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
)


@celery.task(bind=True)
def process_job(self, job_id):
    # Start timing
    start_time = time.time()
    # Import here to avoid circular import
    from app import create_app

    logger.info("Starting processing for job: %s", job_id)
    app = create_app()
    with app.app_context():
        job = Job.query.get(job_id)
        if not job:
            logger.error("Job not found: %s", job_id)
            return

        # Check cache first
        cached_summary = None
        try:
            cached = get_cached_summary(job.content_hash)
            if cached:
                cached_summary = cached.decode()
                logger.info("Cache hit for job %s, hash: %s", job_id, job.content_hash)
        except Exception as e:
            logger.warning("Cache retrieval failed for job %s: %s", job_id, str(e))
            pass

        if cached_summary:
            job.summary = cached_summary
            job.status = JobStatus.COMPLETED
            job.cached = True
            # Calculate processing time
            end_time = time.time()
            job.processing_time_ms = int((end_time - start_time) * 1000)
            commit_pgdb()
            logger.info("Job %s completed from cache", job_id)
            return

        try:
            job.status = JobStatus.PROCESSING
            job.cached = False
            commit_pgdb()
            logger.info("Job %s status updated to PROCESSING", job_id)

            if job.content_type == ContentType.URL:
                logger.info("Fetching content from URL for job %s", job_id)
                content = fetch_url_content(job.content)
            else:
                logger.info("Using text content for job %s", job_id)
                content = job.content

            logger.info("Summarizing content for job %s", job_id)
            summary = summarize(content)

            job.summary = summary
            job.status = JobStatus.COMPLETED

            logger.info("Setting cache for job %s, hash: %s", job_id, job.content_hash)
            set_cached_summary(job.content_hash, summary)

            # Calculate processing time
            end_time = time.time()
            job.processing_time_ms = int((end_time - start_time) * 1000)
            commit_pgdb()

        except Exception as e:
            logger.error("Job %s processing failed: %s", job_id, str(e))
            job.status = JobStatus.FAILED
            commit_pgdb()

        logger.info("Job %s processing completed with status: %s", job_id, job.status)
