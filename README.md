# LLM Reliability Gate

A system to evaluate LLM outputs for reliability, using Bedrock, Elasticsearch, and structured agents.

## Project Structure

- `src/`: Source code
  - `config/`: Configuration management
  - `wrappers/`: API wrappers (Bedrock, Elasticsearch)
  - `agents/`: Core logic agents (T05-T10)
  - `ingest/`: Document ingestion pipeline (T11)
  - `orchestrator.py`: Workflow orchestration (T12)
  - `main.py`: FastAPI application (T13)
- `tests/`: Unit and Integration tests (T15, T16)
- `config.yaml`: Configuration file

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the API server:
   ```bash
   uvicorn src.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

2. key endpoints:
   - `GET /health`: Health check
   - `POST /evaluate`: Run the reliability evaluation workflow
   - `POST /ingest`: Trigger document ingestion

## Running Tests

Run all tests with `pytest`:
```bash
pytest
```

## Configuration

Edit `config.yaml` to change:
- `thresholds`: Risk capabilities
- `evaluation`: Prompt generation settings
- `model`: Bedrock model ID
- `elasticsearch`: Connection details
