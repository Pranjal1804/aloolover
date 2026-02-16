from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.orchestrator import run_workflow, build_response
from src.ingest.pipeline import run_ingest
from src.config.loader import load_config
import uvicorn

app = FastAPI(title="LLM Reliability Gate")


class EvaluationRequest(BaseModel):
    use_case: str = "default"
    config_path: str | None = None  # optional override


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/evaluate")
def evaluate(request: EvaluationRequest):
    """
    Full pipeline: load config → generate prompts → run model → extract claims
    → retrieve evidence → verify claims → score risk → audit log → return result.
    No partial runs. No flags. No debug mode.
    """
    try:
        config = load_config(request.config_path)

        state = {
            "config": config,
            "prompts": [],
            "responses": [],
            "claims": [],
            "evidence": [],
            "verdicts": [],
            "score": {},
        }

        # Full sequential pipeline — every step runs, no shortcuts
        run_workflow(state)

        # Single JSON response, returned exactly once
        response = build_response(state)
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest")
def ingest_documents(clear_first: bool = False):
    try:
        stats = run_ingest(clear_first=clear_first)
        return {"status": "success", "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
