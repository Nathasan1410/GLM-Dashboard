import os
import sys
from zhipuai import ZhipuAI

# The key provided earlier
API_KEY = os.environ.get("ZAI_API_KEY")

if not API_KEY:
    print("No API KEY found in env", file=sys.stderr)
    sys.exit(1)

endpoints = [
    "https://api.z.ai/api/coding/paas/v4",
    "https://api.z.ai/api/paas/v4"
]

# Models likely supported by Coding Plan
models = ["glm-4.7", "glm-4.5", "glm-4.5-air", "glm-5", "glm-3.5-turbo"]

print(f"Testing Key: {API_KEY[:5]}...{API_KEY[-4:]}")

for base_url in endpoints:
    print(f"\n--- Testing Endpoint: {base_url} ---")
    try:
        client = ZhipuAI(api_key=API_KEY, base_url=base_url)
        
        for model in models:
            print(f"  > Pinging model: {model}...", end=" ")
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "ping"}],
                    max_tokens=5
                )
                print(f"SUCCESS! Response: {response.choices[0].message.content}")
                print(f"  *** WORKING CONFIG FOUND ***")
                print(f"  Endpoint: {base_url}")
                print(f"  Model: {model}")
                sys.exit(0)
            except Exception as e:
                # Extract error code if possible
                err_msg = str(e).split('\n')[0]
                print(f"FAILED. Error: {err_msg}")
                
    except Exception as e:
         print(f"  Client Init Failed: {e}")
