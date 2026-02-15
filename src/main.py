from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
from src.orchestrator import run_workflow, build_response
from src.ingest.pipeline import run_ingest
from src.config.loader import load_config
import os
import uvicorn

app = FastAPI(title="LLM Reliability Gate")

class EvaluationRequest(BaseModel):
    use_case: str = "default"
    # Optional overrides, simplifying here
    
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/evaluate")
def evaluate(request: EvaluationRequest):
    """
    Run the reliability evaluation workflow.
    """
    try:
        # Load config
        config = load_config()
        
        # Initialize state
        state = {
            "config": config,
            # Other state keys initialized empty or by agents
            "prompts": [],
            "responses": [],
            "claims": [],
            "evidence": [],
            "verdicts": [],
            "score": {}
        }
        
        # Run workflow
        run_workflow(state)
        
        # Build response
        response = build_response(state)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
def ingest_documents():
    """
    Trigger document ingestion.
    """
    try:
        stats = run_ingest()
        return {"status": "success", "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
