from flask import Blueprint, request, jsonify
from flasgger import swag_from
from app.models import Job, JobStatus, ContentType
from app.services.worker import process_job
from app.utils.helpers import hash_content, write_to_pgdb
from app.swagger import submit_spec, status_spec, result_spec
import urllib.parse
import logging

logger = logging.getLogger(__name__)

# Create API blueprint
api = Blueprint("api", __name__)


@api.route("/submit", methods=["POST"])
@swag_from(submit_spec)
def submit():
    """Submit content for summarization"""
    try:
        data = request.json
        text = data.get("text")
        url = data.get("url")

        # Validate input: must provide text OR url, not both
        if text and url:
            logger.warning("Invalid request: both 'text' and 'url' provided")
            return jsonify({"error": "Provide 'text' or 'url', not both"}), 400
        if not text and not url:
            logger.warning("Invalid request: neither 'text' nor 'url' " "provided")
            return jsonify({"error": "Provide either 'text' or 'url'"}), 400

        # Determine content type and validate
        if url:
            content_type = ContentType.URL
            content = url

            # Validate URL format
            parsed = urllib.parse.urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                logger.warning("Invalid URL format: %s", url)
                return jsonify({"error": "Invalid URL format"}), 400
        else:
            content_type = ContentType.TEXT
            content = text

        # Generate content hash for caching
        content_hash = hash_content(content)
        logger.info("Processing content with hash: %s", content_hash)

        # Create job in database
        try:
            job = Job(
                content_hash=content_hash,
                content_type=content_type,
                content=content,
                status=JobStatus.QUEUED,
            )
            write_to_pgdb(job)
            logger.info("Created job with ID: %s", job.id)
        except Exception as e:
            logger.error("Job creation failed: %s", str(e))
            return jsonify({"error": f"Job creation error: {str(e)}"}), 500

        # Queue job for async processing
        try:
            process_job.delay(job.id)
            logger.info("Queued job %s for processing", job.id)
        except Exception as e:
            logger.error("Job processing queue failed for job %s: %s", job.id, str(e))
            return jsonify({"error": f"Job processing error: {str(e)}"}), 500

        return (
            jsonify(
                {
                    "job_id": job.id,
                    "status": job.status,
                }
            ),
            200,
        )
    except Exception as e:
        logger.exception("Unexpected error in submit endpoint: %s", str(e))
        return jsonify({"error": str(e)}), 500


@api.route("/status/<job_id>")
@swag_from(status_spec)
def status(job_id):
    """Get the current status of a job"""
    try:
        logger.info("Checking status for job: %s", job_id)
        job = Job.query.get(job_id)

        if not job:
            logger.warning("Job not found: %s", job_id)
            return jsonify({"error": "Job not found"}), 404

        logger.info("Job %s status: %s", job_id, job.status)
        return (
            jsonify(
                {
                    "job_id": job.id,
                    "status": job.status,
                    "created_at": job.created_at.isoformat(),
                }
            ),
            200,
        )
    except Exception as e:
        logger.exception("Error checking status for job %s: %s", job_id, str(e))
        return jsonify({"error": str(e)}), 500


@api.route("/result/<job_id>")
@swag_from(result_spec)
def result(job_id):
    """Get the result of a completed job"""
    try:
        logger.info("Retrieving result for job: %s", job_id)
        job = Job.query.get(job_id)

        if not job:
            logger.warning("Job not found for result: %s", job_id)
            return jsonify({"error": "Job not found"}), 404

        if job.status != JobStatus.COMPLETED:
            logger.info("Job %s not ready, status: %s", job_id, job.status)
            return jsonify({"error": "Not ready"}), 400

        logger.info("Returning result for completed job: %s", job_id)
        response_data = {
            "job_id": job.id,
            "summary": job.summary,
            "cached": job.cached,
            "processing_time_ms": job.processing_time_ms,
        }

        # Only include original_url if content type is URL
        if job.content_type == ContentType.URL:
            response_data["original_url"] = job.content

        return jsonify(response_data), 200
    except Exception as e:
        logger.exception("Error retrieving result for job %s: %s", job_id, str(e))
        return jsonify({"error": str(e)}), 500
