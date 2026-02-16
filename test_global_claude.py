import boto3
import json
import os
from dotenv import load_dotenv
from src.wrappers.bedrock import call_llm

load_dotenv()

def test_global_claude():
    model_id = "global.anthropic.claude-haiku-4-5-20251001-v1:0"
    prompt = "Hello, are you Claude 4.5?"
    
    print(f"Testing model: {model_id}")
    try:
        response = call_llm(prompt, model_id_override=model_id)
        print("✅ Success!")
        print(f"Response: {response}")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    test_global_claude()
