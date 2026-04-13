#!/usr/bin/env python3
"""
Verify that the AWS_BEARER_TOKEN_BEDROCK API key is valid and
can successfully call the Bedrock Converse API.
Usage: source .env && python3 scripts/verify-bedrock.py
"""
import os
import sys
import json

try:
    import requests
except ImportError:
    print("❌ 'requests' not installed. Run: pip install requests")
    sys.exit(1)

api_key = os.getenv("AWS_BEARER_TOKEN_BEDROCK", "")
region  = os.getenv("AWS_REGION", "us-east-1")
model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")

print("=" * 55)
print("  Bedrock API Key Verification")
print("=" * 55)
print(f"  Region : {region}")
print(f"  Model  : {model_id}")
print(f"  Key set: {'YES (' + api_key[:8] + '...)' if api_key else 'NO - AWS_BEARER_TOKEN_BEDROCK is empty!'}")
print("=" * 55)

if not api_key:
    print("\n❌ FAIL: Set AWS_BEARER_TOKEN_BEDROCK in your .env and re-run:")
    print("   source .env && python3 scripts/verify-bedrock.py")
    sys.exit(1)

url = f"https://bedrock-runtime.{region}.amazonaws.com/model/{model_id}/converse"
payload = {
    "messages": [
        {"role": "user", "content": [{"text": "Reply with exactly: OK"}]}
    ],
    "inferenceConfig": {"maxTokens": 10, "temperature": 0.0},
}
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",
}

print("\n⏳ Calling Bedrock...")
try:
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    if resp.status_code == 200:
        text = resp.json()["output"]["message"]["content"][0]["text"]
        print(f"✅ SUCCESS — Model replied: {text!r}")
        sys.exit(0)
    else:
        print(f"❌ HTTP {resp.status_code}: {resp.text}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Exception: {e}")
    sys.exit(1)
