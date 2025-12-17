import json
from datetime import datetime

def send_alert(job_id, failure_reason, last_error_details):
    """
    Send alert on hard failure.
    This is a console-based mock implementation.
    In production, this would send an email or webhook.
    """
    alert_payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "job_id": job_id,
        "failure_reason": failure_reason,
        "last_error_details": last_error_details
    }
    
    print("\n" + "=" * 60)
    print("ALERT: WORKFLOW FAILURE")
    print("=" * 60)
    print(json.dumps(alert_payload, indent=2))
    print("=" * 60 + "\n")
