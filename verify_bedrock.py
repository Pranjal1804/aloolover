import boto3
import json
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()

def verify_access():
    region = os.environ.get("AWS_DEFAULT_REGION", "ap-south-1")
    model_id = "apac.anthropic.claude-sonnet-4-20250514-v1:0" # Hardcoded to test specific access
    
    print(f"Testing access to {model_id} in {region}...")
    
    client = boto3.client("bedrock-runtime", region_name=region)
    
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "Hello"}],
    })
    
    try:
        response = client.invoke_model(
            body=body,
            modelId=model_id,
            accept="application/json",
            contentType="application/json"
        )
        print("✅ InvokeModel Success!")
        response_body = json.loads(response.get("body").read())
        print(f"Response: {response_body['content'][0]['text']}")
        return True
    except ClientError as e:
        print(f"❌ InvokeModel Failed: {e}")
        return False

if __name__ == "__main__":
    verify_access()
