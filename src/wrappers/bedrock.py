import boto3
import json
import os
from src.config.loader import load_config
from botocore.exceptions import ClientError

# Global client - initialized on first use or module load if config allows
_bedrock_runtime = None

def _get_client():
    global _bedrock_runtime
    if _bedrock_runtime is None:
        # Check AWS credentials in environment - if specific profile needed, user must set AWS_PROFILE
        # Region defaults to us-east-1 or from env
        region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        _bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name=region)
    return _bedrock_runtime

def call_llm(prompt: str, system: str = "") -> str:
    """
    Call Bedrock LLM with the given prompt and system instruction.
    Uses the model ID from config.yaml.
    """
    config = load_config()
    model_id = config.get("model", {}).get("model_id", "anthropic.claude-v2")
    
    client = _get_client()

    # Construct payload for Claude 3 / 2 (Anthropic format)
    # Note: Different models use different payload structures.
    # This implementation targets Claude generic messages API if supported, or text completion.
    # For robust implementation, we'd handle different providers.
    # Assuming Claude 3 or v2 using messages API or similar.
    
    # Claude 3 Messages API format
    if "claude-3" in model_id or "claude-v2" in model_id or "claude-instant" in model_id:
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
        
        try:
            response = client.invoke_model(
                body=body,
                modelId=model_id,
                accept="application/json",
                contentType="application/json"
            )
            response_body = json.loads(response.get("body").read())
            return response_body["content"][0]["text"]
        except ClientError as e:
            print(f"Error calling Bedrock: {e}")
            raise e
    else:
        # Fallback or other models (e.g. Titan)
        # Simplified for this task
        raise NotImplementedError(f"Model {model_id} not supported in this simple wrapper yet.")

def embed(text: str) -> list[float]:
    """
    Generate embeddings for the given text using Titan Embeddings or similar.
    Defaulting to amazon.titan-embed-text-v1.
    """
    client = _get_client()
    model_id = "amazon.titan-embed-text-v1" # Standard choice
    
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
