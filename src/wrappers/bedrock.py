import boto3
import json
import os
import time
from src.config.loader import load_config
from botocore.exceptions import ClientError

# Global client
_bedrock_runtime = None

def _get_client(region=None):
    global _bedrock_runtime
    
    # If a specific region is requested, we might need a separate client
    # but for simplicity, we'll stick to a primary client unless it's a global call.
    if region is None:
        region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        
    # Always use us-east-1 for global profiles if current region isn't us-east-1
    # or if strictly required by the profile type.
    
    return boto3.client(service_name="bedrock-runtime", region_name=region)

def call_llm(prompt: str, system: str = "", model_id_override: str = None) -> str:
    """
    Call Bedrock LLM.
    Args:
        prompt: The user prompt
        system: System instruction
        model_id_override: Optional model ID to use instead of config default
    """
    if model_id_override:
        model_id = model_id_override
    else:
        config = load_config()
        model_id = config.get("verification_model", {}).get("model_id", "anthropic.claude-v2")

    # Determine region based on model_id
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    if model_id.startswith("global."):
        region = "us-east-1"  # Global profiles typically rooted in us-east-1 or us-west-2
    
    client = _get_client(region=region)
    
    # Claude Messages API format (v3, v2, and inference profiles with 'claude')
    if "claude" in model_id:
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "system": system
        })
        
        # Invoke model with retry logic for throttling
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.invoke_model(
                    modelId=model_id,
                    body=body, # body is already a JSON string
                    accept="application/json",
                    contentType="application/json"
                )
                response_body = json.loads(response.get("body").read())
                
                # Claude 3 (Messages API)
                if "content" in response_body:
                    return response_body["content"][0]["text"]
                # Claude 2 (Completion API)
                elif "completion" in response_body:
                    return response_body["completion"].strip()
                else:
                    return str(response_body)
                    
            except ClientError as e:
                if "ThrottlingException" in str(e) and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"⚠️ Throttled by Bedrock. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                print(f"Error calling Bedrock: {e}")
                raise e
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                raise e
    else:
        # Fallback for Titan Text or others (simplified)
        raise NotImplementedError(f"Model {model_id} interaction not implemented.")

def embed(text: str) -> list[float]:
    """
    Generate embeddings using Titan Embeddings from config or default.
    """
    client = _get_client()
    # Use config or env var for model ID
    model_id = os.environ.get("BEDROCK_EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v1")
    
    body = json.dumps({
        "inputText": text
    })
    
    try:
        response = client.invoke_model(
            body=body,
            modelId=model_id,
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response.get("body").read())
        return response_body["embedding"]
    except ClientError as e:
        print(f"Error calling Bedrock Embeddings: {e}")
        raise e
