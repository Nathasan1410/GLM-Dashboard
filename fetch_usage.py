import os
import time
import jwt
import requests
import json
import sys

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
        print("Error: ZAI_API_KEY environment variable not set")
        sys.exit(1)

    try:
        token = generate_token(api_key, 60)
    except Exception as e:
        print(f"Error generating token: {e}")
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
        
        # Transform the response into our dashboard format
        # Current Z.ai V4 API often returns a structure. We need to adapt it.
        # Assuming the API returns a standard JSON. We'll simply wrap it for now
        # and let the frontend adapt specific fields if we can identify them.
        # Ideally, we should inspect the 'data' structure. 
        # For now, we wrap it exactly as the previous curl command attempted to do,
        # but with valid data.
        
        # Construct the final JSON structure
        output = {
            "lastUpdated": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
            "quotas": []
        }

        # Attempt to parse known Z.ai usage fields if they exist
        # If the API returns a list directly:
        if isinstance(data, list):
            output["quotas"] = data
        # If it returns an object with 'result' or similar:
        elif isinstance(data, dict):
             # Try to normalize some fields into our 'quotas' list format
             # Example: { "total_tokens": 100, ... } -> List of quota objects
             for key, value in data.items():
                 if isinstance(value, (int, float, str)):
                     output["quotas"].append({
                         "title": key.replace("_", " ").title(),
                         "used": value,
                         "limit": 0, # Unknown limit
                         "unit_text": "units"
                     })
                 elif isinstance(value, dict):
                     # Recursive or complex object, try to flatten or ignore
                     pass

        # If data seems empty or we just want to pass it through raw for debugging:
        if not output["quotas"]:
             # Fallback: just dump the raw data as a quota so we see it on the dashboard
             output["quotas"].append({
                 "title": "Raw API Response",
                 "tooltip": "Debugging Info",
                 "used": 0,
                 "limit": 0,
                 "raw_data": json.dumps(data)
             })

        print(json.dumps(output, indent=4))
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
