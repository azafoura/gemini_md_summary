import os

# Gemini API configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAYS = [2, 5, 10]  # seconds
MAX_VALIDATION_ATTEMPTS = 2

# Paths
LOG_FILE = "logs/workflow.log"
OUTPUT_FILE = "output.json"

# Workflow configuration
WORKFLOW_NAME = "gemini_md_summary"
