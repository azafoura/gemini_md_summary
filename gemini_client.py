import json
import time
import hashlib
import requests
from config import GEMINI_API_KEY, MAX_RETRIES, RETRY_DELAYS
from logger import log_event

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"

def call_gemini(content, job_id):
    """
    Call Gemini API with the markdown content.
    Returns parsed JSON response or raises exception.
    Includes retry logic for network errors, 429, and 5xx.
    """
    prompt = f"""Analyze the following Markdown document and return ONLY valid JSON with this exact schema:

{{
  "status": "ok",
  "summary": "1-2 factual sentences summarizing the document",
  "bullet_points": ["key point 1", "key point 2", "key point 3"]
}}

Rules:
- summary: 1-2 factual sentences
- bullet_points: exactly 3 concise key points
- Return ONLY valid JSON, no markdown code fences, no extra text
- Do NOT include word_count or hash_preview fields, they will be computed automatically

Markdown document:
{content}"""

    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "topK": 1,
            "topP": 0.95,
            "maxOutputTokens": 1024
        }
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            log_event(job_id, "API_CALL_STARTED", "info")
            
            url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            # Check for retryable HTTP errors
            if response.status_code == 429 or response.status_code >= 500:
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAYS[attempt]
                    log_event(
                        job_id, 
                        "RETRY_ATTEMPT", 
                        "warning",
                        error_type="http_error",
                        error_message=f"HTTP {response.status_code}, retrying in {delay}s",
                        http_status=response.status_code
                    )
                    time.sleep(delay)
                    continue
                else:
                    log_event(
                        job_id, 
                        "API_CALL_FAILED", 
                        "error",
                        error_type="http_error",
                        error_message=f"HTTP {response.status_code} after {MAX_RETRIES} retries",
                        http_status=response.status_code
                    )
                    raise Exception(f"HTTP {response.status_code} after {MAX_RETRIES} retries")
            
            response.raise_for_status()
            
            result = response.json()
            
            # Extract text from Gemini response structure
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    text = candidate["content"]["parts"][0]["text"].strip()
                    
                    # Remove markdown code fences if present
                    if text.startswith("```json"):
                        text = text[7:]
                    if text.startswith("```"):
                        text = text[3:]
                    if text.endswith("```"):
                        text = text[:-3]
                    text = text.strip()
                    
                    # Parse JSON
                    try:
                        parsed = json.loads(text)
                        
                        # Compute word_count and hash_preview
                        if "summary" in parsed:
                            summary = parsed["summary"]
                            parsed["word_count"] = len(summary.split())
                            parsed["hash_preview"] = hashlib.sha256(summary.encode()).hexdigest()[:8]
                        
                        log_event(job_id, "API_CALL_SUCCESS", "success")
                        return parsed
                    except json.JSONDecodeError as json_err:
                        # Retry on malformed JSON from Gemini
                        if attempt < MAX_RETRIES - 1:
                            delay = RETRY_DELAYS[attempt]
                            log_event(
                                job_id, 
                                "RETRY_ATTEMPT", 
                                "warning",
                                error_type="json_parse_error",
                                error_message=f"Malformed JSON from Gemini: {str(json_err)}, retrying in {delay}s"
                            )
                            time.sleep(delay)
                            continue
                        else:
                            log_event(
                                job_id, 
                                "API_CALL_FAILED", 
                                "error",
                                error_type="json_parse_error",
                                error_message=f"{str(json_err)} after {MAX_RETRIES} retries"
                            )
                            raise
            
            raise Exception("Unexpected response structure from Gemini API")
            
        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAYS[attempt]
                log_event(
                    job_id, 
                    "RETRY_ATTEMPT", 
                    "warning",
                    error_type="network_error",
                    error_message=f"{str(e)}, retrying in {delay}s"
                )
                time.sleep(delay)
                continue
            else:
                log_event(
                    job_id, 
                    "API_CALL_FAILED", 
                    "error",
                    error_type="network_error",
                    error_message=f"{str(e)} after {MAX_RETRIES} retries"
                )
                raise
        except Exception as e:
            log_event(
                job_id, 
                "API_CALL_FAILED", 
                "error",
                error_type="unexpected_error",
                error_message=str(e)
            )
            raise
    
    raise Exception(f"Failed after {MAX_RETRIES} retries")
