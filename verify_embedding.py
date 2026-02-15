import boto3
import json
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()

def verify_embedding():
    region = os.environ.get("AWS_DEFAULT_REGION", "ap-south-1")
    model_id = os.environ.get("BEDROCK_EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2:0")
    
    print(f"Testing embedding access to {model_id} in {region}...")
    
    client = boto3.client("bedrock-runtime", region_name=region)
    
    body = json.dumps({
        "inputText": "Hello world"
    })
    
    try:
        response = client.invoke_model(
            body=body,
            modelId=model_id,
            accept="application/json",
            contentType="application/json"
        )
        print("✅ Embed InvokeModel Success!")
        response_body = json.loads(response.get("body").read())
        embedding = response_body.get("embedding")
        print(f"Embedding length: {len(embedding)}")
        return True
    except ClientError as e:
        print(f"❌ Embed InvokeModel Failed: {e}")
        return False

if __name__ == "__main__":
    verify_embedding()
