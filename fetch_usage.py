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

    # Minimal payload to ping the model
    payload = {
        "model": "glm-4",
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 1
    }

    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, json=payload)
        end_time = time.time()
        
        # Calculate latency in milliseconds
        latency_ms = int((end_time - start_time) * 1000)
        
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
                    "tooltip": "Verifies that your API Key is valid and the Z.ai service is reachable."
                },
                {
                    "title": "Latency",
                    "used": latency_ms,
                    "limit": 1000, # Arbitrary 'good' limit for visual bar
                    "unit_text": "ms",
                    "tooltip": "Round-trip time to generate a minimal response."
                },
                {
                    "title": "Model Reachability",
                    "used": "GLM-4",
                    "limit": 0,
                    "unit_text": "Verified",
                    "tooltip": "Successfully connected to the GLM-4 model."
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
                }
            ]
        }
        print(json.dumps(output, indent=4))
        sys.exit(0) # Exit cleanly so the workflow doesn't 'fail', but updates the dashboard with the error state
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
