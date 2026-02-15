import os
import requests
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv

load_dotenv()

def check_aws():
    print("Checking AWS Credentials...")
    try:
        # Check basic credentials presence
        session = boto3.Session()
        credentials = session.get_credentials()
        if not credentials:
             print("❌ AWS Credentials not found.")
             return False
        
        # Check Bedrock access (list foundation models)
        region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        print(f"  Region: {region}")
        client = boto3.client("bedrock", region_name=region)
        try:
            client.list_foundation_models()
            print("✅ AWS Bedrock Access: OK")
            return True
        except ClientError as e:
            print(f"❌ AWS Bedrock Access Failed: {e}")
            return False
            
    except NoCredentialsError:
         print("❌ AWS Credentials not found.")
         return False
    except Exception as e:
         print(f"❌ AWS Check Failed: {e}")
         return False

def check_es():
    print("\nChecking Elasticsearch...")
    try:
        response = requests.get("http://localhost:9200")
        if response.status_code == 200:
            print("✅ Elasticsearch: OK")
            return True
        else:
            print(f"❌ Elasticsearch returned status: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ Elasticsearch: Connection Refused (Is it running?)")
        return False

def check_ollama():
    print("\nChecking Ollama...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("✅ Ollama: OK")
            return True
        else:
             print(f"⚠️ Ollama returned status: {response.status_code}")
             return False
    except requests.exceptions.Timeout:
        print("❌ Ollama: Timeout (Is it running?)")
        return False
    except requests.ConnectionError:
        print("❌ Ollama: Connection Refused (Is it running?)")
        return False

if __name__ == "__main__":
    aws_ok = check_aws()
    es_ok = check_es()
    ollama_ok = check_ollama()
    
    print("\n--- Summary ---")
    if not aws_ok:
        print("⚠️  You need to configure AWS Credentials for Bedrock.")
    if not es_ok:
        print("⚠️  You need to start Elasticsearch (docker compose up -d).")
    if not ollama_ok:
        print("ℹ️  Ollama is not detected. 'target_model: ollama' will fail.")
        print("   Consider changing config.yaml to use 'provider: bedrock' if you have access.")
