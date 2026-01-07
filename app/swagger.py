"""
Swagger documentation specifications for API endpoints
"""

submit_spec = {
    "tags": ["Summarization"],
    "description": "Submit content for summarization",
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Plain text content to summarize "
                        "(use either text or url, not both)",
                        "example": "This is a sample text that needs to "
                        "be summarized.",
                    },
                    "url": {
                        "type": "string",
                        "description": "URL of content to fetch and "
                        "summarize (use either text or url, "
                        "not both)",
                        "example": "https://example.com/article",
                    },
                },
            },
        }
    ],
    "responses": {
        "200": {
            "description": "Job created successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "Job ID for tracking",
                        "example": "abc123-def456-ghi789",
                    },
                    "status": {
                        "type": "string",
                        "description": "Initial job status",
                        "example": "queued",
                    },
                },
            },
        },
        "400": {
            "description": "Invalid request",
            "schema": {
                "type": "object",
                "properties": {"error": {"type": "string"}},
            },
        },
        "500": {
            "description": "Server error",
            "schema": {
                "type": "object",
                "properties": {"error": {"type": "string"}},
            },
        },
    },
}

status_spec = {
    "tags": ["Summarization"],
    "description": "Get job status",
    "parameters": [
        {
            "in": "path",
            "name": "job_id",
            "type": "string",
            "required": True,
            "description": "Job ID to check status for",
            "example": "abc123-def456-ghi789",
        }
    ],
    "responses": {
        "200": {
            "description": "Job status retrieved successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "The job ID",
                        "example": "abc123-def456-ghi789",
                    },
                    "status": {
                        "type": "string",
                        "description": "Current job status",
                        "enum": ["queued", "processing", "completed", "failed"],
                        "example": "completed",
                    },
                    "created_at": {
                        "type": "string",
                        "description": "Job creation timestamp in ISO format",
                        "example": "2026-01-07T10:30:00.123456",
                    },
                },
            },
        },
        "404": {
            "description": "Job not found",
            "schema": {
                "type": "object",
                "properties": {"error": {"type": "string"}},
            },
        },
        "500": {
            "description": "Server error",
            "schema": {
                "type": "object",
                "properties": {"error": {"type": "string"}},
            },
        },
    },
}

result_spec = {
    "tags": ["Summarization"],
    "description": "Get summarization result",
    "parameters": [
        {
            "in": "path",
            "name": "job_id",
            "type": "string",
            "required": True,
            "description": "Job ID to retrieve result for",
            "example": "abc123-def456-ghi789",
        }
    ],
    "responses": {
        "200": {
            "description": "Summary retrieved successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "The job ID",
                        "example": "abc123-def456-ghi789",
                    },
                    "original_url": {
                        "type": "string",
                        "description": "The original URL (only included "
                        "if content type is URL)",
                        "example": "https://example.com/article",
                    },
                    "summary": {
                        "type": "string",
                        "description": "The generated summary",
                        "example": "This article discusses the " "importance of...",
                    },
                    "cached": {
                        "type": "boolean",
                        "description": "Whether the result was retrieved " "from cache",
                        "example": False,
                    },
                    "processing_time_ms": {
                        "type": "integer",
                        "description": "Processing time in milliseconds",
                        "example": 2340,
                    },
                },
                "required": ["job_id", "summary", "cached", "processing_time_ms"],
            },
        },
        "400": {
            "description": "Job not ready yet",
            "schema": {
                "type": "object",
                "properties": {"error": {"type": "string"}},
            },
        },
        "404": {
            "description": "Job not found",
            "schema": {
                "type": "object",
                "properties": {"error": {"type": "string"}},
            },
        },
        "500": {
            "description": "Server error",
            "schema": {
                "type": "object",
                "properties": {"error": {"type": "string"}},
            },
        },
    },
}
