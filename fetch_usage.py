import os
import time
import jwt
import requests
import json
import sys
import warnings

# Suppress the weak key warning from pyjwt
warnings.filterwarnings("ignore", category=UserWarning, module='jwt')

def generate_token(apikey: str, exp_seconds: int):
    try:
        id, secret = apikey.split(".")
    except Exception as e:
        raise Exception("Invalid API Key format", e)

    payload = {
        "api_key": id,
        "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
        "timestamp": int(round(time.time() * 1000)),
    }

    return jwt.encode(
        payload,
        secret.encode("utf-8"),
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )

def main():
    api_key = os.environ.get("ZAI_API_KEY")
    if not api_key:
        print("Error: ZAI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    try:
        token = generate_token(api_key, 60)
    except Exception as e:
        print(f"Error generating token: {e}", file=sys.stderr)
        sys.exit(1)

    # API Endpoint for Chat Completions (used as a ping)
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Use 'glm-4-flash' as it is often free/cheaper and more likely to be available
    # Increased max_tokens to 5 to avoid potential boundary issues with 1
    payload = {
        "model": "glm-4-flash",
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 5
    }

    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, json=payload)
        end_time = time.time()
        
        # Calculate latency in milliseconds
        latency_ms = int((end_time - start_time) * 1000)
        
        # DEBUG: Print the response content for debugging 400 errors
        if response.status_code >= 400:
             print(f"DEBUG: API Error {response.status_code}", file=sys.stderr)
             print(f"DEBUG: Response Body: {response.text}", file=sys.stderr)

        response.raise_for_status()
        
        # If we get here, the API is working
        api_status = "Operational"
        
        # Construct the final JSON structure for the dashboard
        output = {
            "lastUpdated": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
            "quotas": [
                {
                    "title": "API Status",
                    "used": api_status,
                    "limit": 0,
                    "unit_text": "State",
                    "tooltip": "Verifies that your API Key is working via glm-4-flash."
                },
                {
                    "title": "Latency",
                    "used": latency_ms,
                    "limit": 1000, 
                    "unit_text": "ms",
                    "tooltip": "Round-trip time to generate a response."
                },
                {
                    "title": "Model Reachability",
                    "used": "GLM-4 Flash",
                    "limit": 0,
                    "unit_text": "Verified",
                    "tooltip": "Successfully connected to the GLM-4 Flash model."
                }
            ]
        }

        print(json.dumps(output, indent=4))
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}", file=sys.stderr)
        # Output a "Down" status to the dashboard
        output = {
            "lastUpdated": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
            "quotas": [
                 {
                    "title": "API Status",
                    "used": "Error",
                    "limit": 0,
                    "unit_text": str(e.response.status_code)
                },
                {
                    "title": "Error Details",
                    "used": "Check Logs",
                    "limit": 0,
                    "unit_text": "Action Logs",
                    "tooltip": "See GitHub Action logs for full error details."
                }
            ]
        }
        print(json.dumps(output, indent=4))
        sys.exit(0) 
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
