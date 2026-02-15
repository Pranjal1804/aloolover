# LLM Reliability Gate

A system to evaluate LLM outputs for reliability, using Bedrock, Elasticsearch, and structured agents.

## Project Structure

- `src/`: Source code including agents, config, ingestion, and API.
- `docker-compose.yml`: Local Elasticsearch & Kibana setup.
- `config.yaml`: Configuration for models and thresholds.

## Checklist: What has been implemented & verified

- [x] **FastAPI Backend**: Running at `http://localhost:8000`
- [x] **Elasticsearch**: Running locally via Docker (`http://localhost:9200`)
- [x] **Ollama Wrapper**: Implemented for testing local models
- [x] **Doc Ingestion**: Ready (`src/ingest/pipeline.py`)
- [x] **Verification Agent**: Connects to Bedrock (Claude)

## ⚠️ Action Required: Add API Keys

The system requires AWS credentials to use Bedrock for:
1.  **Verification**: Using `anthropic.claude-v2` to check claims.
2.  **Ingestion**: Using `amazon.titan-embed-text-v1` to create embeddings.

### How to configure keys:

1.  **Copy the example file**:
    ```bash
    cp .env.example .env
    ```

2.  **Edit `.env`** and add your AWS credentials:
    ```bash
    AWS_ACCESS_KEY_ID="<YOUR_KEY>"
    AWS_SECRET_ACCESS_KEY="<YOUR_SECRET>"
    AWS_DEFAULT_REGION="ap-south-1"  # Ensure this region has Bedrock enabled
    ```

3.  **Export them** (or restart the app to pick up `.env`):
    ```bash
    source .env
    export AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_DEFAULT_REGION
    ```

## 🚀 How to Run

1.  **Start Dependencies**
    Ensure Elasticsearch and Ollama are running:
    ```bash
    # Check status
    python3 check_env.py
    ```
    If missing, start Elastic:
    ```bash
    sudo docker compose up -d
    ```

2.  **Prepare Ollama** (Target Model)
    Pull the model specified in `config.yaml` (default: `llama3`):
    ```bash
    ollama pull llama3
    ```

3.  **Ingest Data**
    Load your trusted documents into the system:
    ```bash
    # Create sample data if needed
    mkdir -p data/docs
    echo "The capital of France is Paris." > data/docs/sample.txt
    
    # Run ingestion
    curl -X POST http://localhost:8000/ingest
    ```

4.  **Run Evaluation**
    Test if the model is hallucinating:
    ```bash
    curl -X POST http://localhost:8000/evaluate \
      -H "Content-Type: application/json" \
      -d '{"use_case": "demo"}'
    ```

## Troubleshooting

-   **"Unable to locate credentials"**: AWS keys are missing from environment.
-   **"Connection refused"**: Elasticsearch or Ollama is not running.
-   **"Model not found"**: Run `ollama list` and ensure `llama3` is pulled.
