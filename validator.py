import hashlib
from logger import log_event

def validate_response(response, job_id):
    """
    Validate the Gemini response against the required schema.
    Returns True if valid, False otherwise.
    """
    required_fields = ["status", "summary", "bullet_points", "word_count", "hash_preview"]
    
    # Check all required fields exist
    for field in required_fields:
        if field not in response:
            log_event(
                job_id,
                "RESPONSE_VALIDATION_FAILED",
                "error",
                error_type="missing_field",
                error_message=f"Missing required field: {field}"
            )
            return False
    
    # Validate bullet_points length
    if not isinstance(response["bullet_points"], list) or len(response["bullet_points"]) != 3:
        log_event(
            job_id,
            "RESPONSE_VALIDATION_FAILED",
            "error",
            error_type="invalid_bullet_points",
            error_message=f"bullet_points must be exactly 3 items, got {len(response.get('bullet_points', []))}"
        )
        return False
    
    # Validate word_count
    summary = response["summary"]
    actual_word_count = len(summary.split())
    reported_word_count = response["word_count"]
    
    if actual_word_count != reported_word_count:
        log_event(
            job_id,
            "RESPONSE_VALIDATION_FAILED",
            "error",
            error_type="word_count_mismatch",
            error_message=f"word_count mismatch: expected {actual_word_count}, got {reported_word_count}"
        )
        return False
    
    # Validate hash_preview
    computed_hash = hashlib.sha256(summary.encode()).hexdigest()[:8]
    reported_hash = response["hash_preview"]
    
    if computed_hash != reported_hash:
        log_event(
            job_id,
            "RESPONSE_VALIDATION_FAILED",
            "error",
            error_type="hash_mismatch",
            error_message=f"hash_preview mismatch: expected {computed_hash}, got {reported_hash}"
        )
        return False
    
    log_event(job_id, "RESPONSE_VALIDATION_SUCCESS", "success")
    return True
