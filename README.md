# Async Content Summarizer

A Flask-based service that accepts URLs or text content, processes them asynchronously using Celery workers, and returns AI-generated summaries. The service uses Redis for task queuing and caching, PostgreSQL for job persistence, and GitHub Models API for AI-powered summarization.

## Features

- 📝 **Dual Input Support**: Submit URLs or plain text for summarization
- ⚡ **Asynchronous Processing**: Non-blocking job processing with Celery
- 💾 **Smart Caching**: Redis-based caching to avoid re-processing identical content
- 📊 **Job Tracking**: Monitor job status (QUEUED, PROCESSING, COMPLETED, FAILED)
- 🤖 **AI-Powered**: Leverages GitHub Models API for intelligent summarization
- 📖 **Interactive API Docs**: Built-in Swagger UI for easy API exploration
- 🔍 **Content Extraction**: Automatic web scraping for URL-based submissions

## Architecture

- **Flask**: Web framework for REST API
- **Celery**: Distributed task queue for async processing
- **Redis**: Message broker and caching layer
- **PostgreSQL**: Persistent storage for jobs and results
- **GitHub Models**: AI model endpoint for text summarization
- **BeautifulSoup4**: HTML parsing and content extraction

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** (check with `python --version`)
- **PostgreSQL** (version 12 or higher)
- **Redis** (version 5 or higher)
- **Git**

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd async-summarizer
```

### 2. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Redis Server

```bash
sudo apt install redis-server
```

### 5. Set Up PostgreSQL Database

```bash
# Log into PostgreSQL
psql -U postgres

# Create the database
CREATE DATABASE async_summarizer;

# Exit PostgreSQL
\q
```

Alternatively, you can use the provided SQL script:

```bash
psql -U postgres -f create_db.sql
```

### 6. Configure Environment Variables

Create a `.env` file in the project root directory by copying the example:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
FLASK_ENV=development

DATABASE_URL=postgresql://postgres:your_password@localhost:5432/async_summarizer

REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

LLM_TOKEN=your_github_personal_access_token
LLM_ENDPOINT=https://models.github.ai/inference
LLM_MODEL=openai/gpt-4o
```

**Important**: 
- Replace `your_password` with your PostgreSQL password
- Replace `your_github_personal_access_token` with your actual GitHub PAT (with appropriate scopes for GitHub Models)
- Update `LLM_MODEL` if you want to use a different model

---

## Running the Application

The application requires **two terminals** to run simultaneously:

### Terminal 1: Celery Worker (Background Job Processor)

```bash
# Activate virtual environment
source venv/bin/activate

# Start Redis server (if not running as a service)
redis-server

# In a new terminal tab/window with activated venv:
celery -A app.services.worker worker --loglevel=info
```

### Terminal 2: Flask Application (API Server)

```bash
# Activate virtual environment
source venv/bin/activate

# Start Flask development server
flask run
```

The application will be available at `http://localhost:5000`

---

## Project Structure

```
async-summarizer/
├── app/
│   ├── __init__.py            # Flask app factory
│   ├── config.py              # Configuration management
│   ├── models.py              # Database models
│   ├── routes.py              # API endpoints
│   ├── swagger.py             # Swagger/OpenAPI specs
│   ├── services/
│   │   ├── __init__.py        # Services package init
│   │   ├── cache_service.py   # Redis caching logic
│   │   ├── content_fetcher.py # URL content extraction
│   │   ├── summarizer.py      # AI summarization logic
│   │   └── worker.py          # Celery task (worker)
│   └── utils/
│       ├── __init__.py        # Utils package init
│       └── helpers.py         # Utility functions
├── .env                       # Environment variables (create this)
├── .env.example               # Example environment file
├── create_db.sql              # Database creation
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## API Documentation

Once the application is running, you can access the interactive Swagger UI documentation at:

```
http://localhost:5000/swagger/
```

### API Endpoints

#### 1. Submit Content for Summarization

**Endpoint**: `POST /submit`

**Description**: Submit content for summarization. You can provide either a URL or plain text, but not both.

**Request Body** (URL):
```json
{
  "url": "https://example.com/article"
}
```

**Request Body** (Text):
```json
{
  "text": "Your long text content here..."
}
```

**Success Response** (200 OK):
```json
{
  "job_id": "abc123-def456-ghi789",
  "status": "queued"
}
```

**Error Responses**:
- **400 Bad Request** - When both `text` and `url` are provided, or neither is provided, or URL format is invalid:
  ```json
  {
    "error": "Provide 'text' or 'url', not both"
  }
  ```
- **500 Internal Server Error** - When job creation or queuing fails:
  ```json
  {
    "error": "Job creation error: <error details>"
  }
  ```

---

#### 2. Check Job Status

**Endpoint**: `GET /status/<job_id>`

**Description**: Get the current status of a submitted job.

**Parameters**:
- `job_id` (path parameter): The job ID returned from the `/submit` endpoint

**Success Response** (200 OK):
```json
{
  "job_id": "abc123-def456-ghi789",
  "status": "processing",
  "created_at": "2026-01-07T10:30:00.123456"
}
```

**Status Values**: 
- `queued` - Job is waiting to be processed
- `processing` - Job is currently being processed
- `completed` - Job has finished successfully
- `failed` - Job processing failed

**Error Responses**:
- **404 Not Found** - Job ID doesn't exist:
  ```json
  {
    "error": "Job not found"
  }
  ```
- **500 Internal Server Error** - Server error:
  ```json
  {
    "error": "<error details>"
  }
  ```

---

#### 3. Get Summarization Result

**Endpoint**: `GET /result/<job_id>`

**Description**: Retrieve the summarization result for a completed job.

**Parameters**:
- `job_id` (path parameter): The job ID returned from the `/submit` endpoint

**Success Response** (200 OK) - For URL content:
```json
{
  "job_id": "abc123-def456-ghi789",
  "original_url": "https://example.com/article",
  "summary": "This article discusses the importance of...",
  "cached": false,
  "processing_time_ms": 2340
}
```

**Success Response** (200 OK) - For text content:
```json
{
  "job_id": "abc123-def456-ghi789",
  "summary": "The provided text discusses...",
  "cached": true,
  "processing_time_ms": 150
}
```

**Response Fields**:
- `job_id`: The unique identifier for the job
- `original_url`: The original URL (only included when content type is URL)
- `summary`: The AI-generated summary of the content
- `cached`: Boolean indicating if the result was retrieved from cache
- `processing_time_ms`: Processing time in milliseconds

**Error Responses**:
- **400 Bad Request** - Job is not yet completed:
  ```json
  {
    "error": "Not ready"
  }
  ```
- **404 Not Found** - Job ID doesn't exist:
  ```json
  {
    "error": "Job not found"
  }
  ```
- **500 Internal Server Error** - Server error:
  ```json
  {
    "error": "<error details>"
  }
  ```

---

## Troubleshooting

### Redis Connection Issues
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# If not running, start Redis
redis-server
```

### PostgreSQL Connection Issues
```bash
# Test database connection
psql -U postgres -d async_summarizer -c "SELECT 1;"

# Check if database exists
psql -U postgres -c "\l" | grep async_summarizer
```

### Celery Worker Not Starting
- Ensure Redis is running
- Check that virtual environment is activated
- Verify `CELERY_BROKER_URL` in `.env` is correct

### GitHub Models API Issues
- Verify your `LLM_TOKEN` is valid
- Check token has appropriate scopes
- Ensure the model name is correct and available

---
