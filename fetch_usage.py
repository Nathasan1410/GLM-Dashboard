import os
import sys
import json
import time

try:
    from zhipuai import ZhipuAI
except Exception as e:
    print(f"Error importing zhipuai: {type(e).__name__}: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

def main():
    api_key = os.environ.get("ZAI_API_KEY")
    if not api_key:
        print("Error: ZAI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Use the specific endpoint for Z.ai Coding Plan
    client = ZhipuAI(
        api_key=api_key, 
        base_url="https://api.z.ai/api/coding/paas/v4"
    )

    try:
        start_time = time.time()
        # Ping check using a known working model for this plan
        response = client.chat.completions.create(
            model="glm-4.7",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=6,
        )
        end_time = time.time()
        
        latency_ms = int((end_time - start_time) * 1000)
        api_status = "Operational"

        output = {
            "lastUpdated": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
            "quotas": [
                {
                    "title": "API Status",
                    "used": api_status,
                    "limit": 0,
                    "unit_text": "State",
                    "tooltip": "Verifies that your API Key is working via glm-4.7."
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
                    "used": "GLM-4.7",
                    "limit": 0,
                    "unit_text": "Verified",
                    "tooltip": "Successfully connected to the GLM-4.7 model."
                }
            ]
        }
        print(json.dumps(output, indent=4))

    except Exception as e:
        print(f"API Error: {e}", file=sys.stderr)
        
        status_code = "Error"
        # Try to extract a meaningful error code
        # ZhipuAI exceptions often have a 'code' or 'status_code' attribute
        if hasattr(e, 'status_code'):
             status_code = str(e.status_code)
        elif hasattr(e, 'code'):
             status_code = str(e.code)
             
        output = {
            "lastUpdated": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
            "quotas": [
                 {
                    "title": "API Status",
                    "used": "Error",
                    "limit": 0,
                    "unit_text": status_code
                },
                {
                    "title": "Error Message",
                    "used": "Check Logs",
                    "limit": 0,
                    "unit_text": "See Console",
                    "tooltip": str(e)[:100] # Truncate long error messages for tooltip
                }
            ]
        }
        print(json.dumps(output, indent=4))
        sys.exit(0)

if __name__ == "__main__":
    main()
