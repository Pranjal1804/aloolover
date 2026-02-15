import boto3
import json
import os
from src.config.loader import load_config
from botocore.exceptions import ClientError

# Global client
_bedrock_runtime = None

def _get_client():
    global _bedrock_runtime
    if _bedrock_runtime is None:
        region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        _bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name=region)
    return _bedrock_runtime

def call_llm(prompt: str, system: str = "", model_id_override: str = None) -> str:
    """
    Call Bedrock LLM.
    Args:
        prompt: The user prompt
        system: System instruction
        model_id_override: Optional model ID to use instead of config default
    """
    client = _get_client()
    
    if model_id_override:
        model_id = model_id_override
    else:
        config = load_config()
        # Default to verification model if not specified
        model_id = config.get("verification_model", {}).get("model_id", "anthropic.claude-v2")
    
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
