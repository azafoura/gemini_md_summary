import json
import os
from datetime import datetime
from config import LOG_FILE, WORKFLOW_NAME

def log_event(job_id, step_name, status, error_type=None, error_message=None, http_status=None):
    """Write a flat JSON log entry to the log file."""
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "workflow_name": WORKFLOW_NAME,
        "job_id": job_id,
        "step": step_name,
        "status": status
    }
    
    if error_type:
        event["error_type"] = error_type
    if error_message:
        event["error_message"] = error_message
    if http_status:
        event["http_status"] = http_status
    
    # Ensure the logs directory exists
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")
