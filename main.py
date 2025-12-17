import uuid
import sys
import json
import argparse
from config import OUTPUT_FILE, MAX_VALIDATION_ATTEMPTS
from logger import log_event
from gemini_client import call_gemini
from validator import validate_response
from alert import send_alert

def main():
    """Main workflow orchestration."""
    parser = argparse.ArgumentParser(description="Gemini Markdown Summary Workflow")
    parser.add_argument("-i", "--input", required=True, help="Path to input Markdown file")
    args = parser.parse_args()
    
    input_file = args.input
    job_id = str(uuid.uuid4())
    
    log_event(job_id, "WORKFLOW_STARTED", "info")
    
    try:
        # Load input file
        log_event(job_id, "LOAD_INPUT", "info")
        with open(input_file, "r") as f:
            content = f.read()
        
        # Call Gemini API (includes retry logic)
        response = call_gemini(content, job_id)
        
        # Validate response
        validation_failures = 0
        
        while validation_failures < MAX_VALIDATION_ATTEMPTS:
            if validate_response(response, job_id):
                # Success - save output
                with open(OUTPUT_FILE, "w") as f:
                    json.dump(response, f, indent=2)
                
                log_event(job_id, "WORKFLOW_COMPLETED", "success")
                print(f"\nWorkflow completed successfully (job_id: {job_id})")
                print(f"Summary: {response['summary']}")
                print(f"Bullet points: {response['bullet_points']}")
                print(f"Output saved to: {OUTPUT_FILE}")
                sys.exit(0)
            else:
                validation_failures += 1
                if validation_failures < MAX_VALIDATION_ATTEMPTS:
                    log_event(job_id, "RETRY_VALIDATION", "warning")
                    # Retry the API call
                    response = call_gemini(content, job_id)
        
        # Validation failed twice
        failure_reason = "Validation failed after 2 attempts"
        last_error = "Response schema validation failed"
        log_event(job_id, "WORKFLOW_FAILED", "error", error_type="validation_failure", error_message=failure_reason)
        send_alert(job_id, failure_reason, last_error)
        sys.exit(1)
        
    except Exception as e:
        # Hard failure after retries exhausted
        failure_reason = f"Exception: {type(e).__name__}"
        last_error = str(e)
        log_event(job_id, "WORKFLOW_FAILED", "error", error_type="exception", error_message=last_error)
        send_alert(job_id, failure_reason, last_error)
        sys.exit(1)

if __name__ == "__main__":
    main()
