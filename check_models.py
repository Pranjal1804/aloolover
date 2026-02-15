import boto3
import json
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()

def check_model(model_id):
    region = os.environ.get("AWS_DEFAULT_REGION", "ap-south-1")
    print(f"\nTesting access to {model_id} in {region}...")
    
    client = boto3.client("bedrock-runtime", region_name=region)
    
    # Simple payload for Claude 3 family
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "Hi"}],
    })
    
    try:
        response = client.invoke_model(
            body=body,
            modelId=model_id,
            accept="application/json",
            contentType="application/json"
        )
        print(f"✅ Success! {model_id} is available.")
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"❌ Failed: {error_code} - {e.response['Error']['Message']}")
        return False

if __name__ == "__main__":
    # List of likely models in ap-south-1
    candidates = [
        "anthropic.claude-3-haiku-20240307-v1:0",
        "anthropic.claude-3-sonnet-20240229-v1:0",
        "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "anthropic.claude-v2"
    ]
    
    working_model = None
    for model in candidates:
        if check_model(model):
            working_model = model
            break
            
    if working_model:
        print(f"\n✨ FOUND WORKING MODEL: {working_model}")
        print("I will update config.yaml to use this model.")
    else:
        print("\n⚠️ No Claude models are currently enabled for this IAM user in this region.")
        print("Please go to AWS Console -> Bedrock -> Model access and enable Claude.")
