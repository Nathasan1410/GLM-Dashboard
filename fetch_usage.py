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

    url = "https://open.bigmodel.cn/api/paas/v4/usage"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # DEBUG: Print raw response to stderr so it shows in GitHub Action logs
        print("DEBUG RAW RESPONSE form Z.ai:", file=sys.stderr)
        print(json.dumps(data, indent=2), file=sys.stderr)
        
        # Construct the final JSON structure
        output = {
            "lastUpdated": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
            "quotas": []
        }

        # Attempt to parse known Z.ai usage fields
        # Structure usually is: { "total_tokens": 100, ... } or { "result": ... }
        if isinstance(data, dict):
             for key, value in data.items():
                 # Filter out complex objects, keep simple stats
                 if isinstance(value, (int, float)):
                     output["quotas"].append({
                         "title": key.replace("_", " ").title(),
                         "used": value,
                         "limit": 0, # Z.ai often doesn't return limit in usage endpoint
                         "unit_text": "units"
                     })
                 elif isinstance(value, str):
                     # Maybe a string value?
                     pass

        # If we couldn't parse anything useful, add the raw data as a card
        if not output["quotas"]:
             output["quotas"].append({
                 "title": "Raw Data (parsing failed)",
                 "tooltip": "Check logs",
                 "used": 0,
                 "limit": 0,
                 "unit_text": "Check Action Logs"
             })

        print(json.dumps(output, indent=4))
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}", file=sys.stderr)
        print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
