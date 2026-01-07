import time
import functools
import hashlib
import logging
from sqlalchemy.exc import OperationalError
from psycopg2 import OperationalError as Psycopg2OperationalError
from app.models import db

logger = logging.getLogger(__name__)


def generic_retry(max_attempts=3, delay=5):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    time.sleep(delay)
            raise last_exc

        return wrapper

    return decorator


def hash_content(text):
    return hashlib.sha256(text.encode()).hexdigest()


MAX_RETRIES = 3
RETRY_WAIT_SECONDS = 2


def retry_on_pgdb_exception(func):

    def wrapper(*args, **kwargs):
        retries = 0
        while retries < MAX_RETRIES:
            try:
                return func(*args, **kwargs)
            except (OperationalError, Psycopg2OperationalError) as e:
                logger.error("OperationalError: %s", e)
                retries += 1
                if retries < MAX_RETRIES:
                    logger.info("Retrying... (%d/%d)", retries, MAX_RETRIES)
                    time.sleep(RETRY_WAIT_SECONDS)
                else:
                    logger.error(
                        "Max retries reached. Could not execute the operation."
                    )
                    raise
            except Exception as e:
                logger.exception("An unexpected error occurred: %s", e)
                raise

        return None

    return wrapper


@retry_on_pgdb_exception
def write_to_pgdb(obj):
    db.session.add(obj)
    db.session.commit()


@retry_on_pgdb_exception
def delete_from_pgdb(obj):
    db.session.delete(obj)
    db.session.commit()


@retry_on_pgdb_exception
def commit_pgdb():
    db.session.commit()
