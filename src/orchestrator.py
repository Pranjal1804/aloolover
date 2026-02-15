from src.agents.score_risk import score_risk
from src.agents.generate_prompts import generate_prompts
from src.agents.run_model import run_model
from src.agents.extract_claims import extract_claims
from src.agents.retrieve_evidence import retrieve_evidence
from src.agents.verify_claims import verify_claims
from src.wrappers.elasticsearch_helper import index_doc
import uuid
from datetime import datetime


def run_workflow(state: dict) -> None:
    """
    Run the complete evaluation workflow. Sequential. No async.
    Updates state in-place.
    """
    run_id = str(uuid.uuid4())
    state["run_id"] = run_id
    state["timestamp"] = datetime.utcnow().isoformat()

    print("Step 1: Generating Prompts...")
    generate_prompts(state)

    print("Step 2: Running Model...")
    run_model(state)

    print("Step 3: Extracting Claims...")
    extract_claims(state)

    print("Step 4: Retrieving Evidence...")
    retrieve_evidence(state)

    print("Step 5: Verifying Claims...")
    verify_claims(state)

    print("Step 6: Scoring Risk...")
    score_risk(state)

    # Step 7 — Audit log to Elasticsearch
    print("Step 7: Audit Logging...")
    try:
        log_entry = {
            "run_id": run_id,
            "timestamp": state["timestamp"],
            "config_use_case": state.get("config", {}).get("use_case", ""),
            "target_model": state.get("config", {}).get("target_model", {}),
            "num_prompts": len(state.get("prompts", [])),
            "num_responses": len(state.get("responses", [])),
            "num_claims": len(state.get("claims", [])),
            "num_verdicts": len(state.get("verdicts", [])),
            "score": state.get("score", {}),
            "prompts": state.get("prompts", []),
            "responses": state.get("responses", []),
            "claims": state.get("claims", []),
            "verdicts": state.get("verdicts", []),
        }
        index_doc("evaluation_runs", run_id, log_entry)
        print(f"Run {run_id} logged to Elasticsearch.")
    except Exception as e:
        print(f"Failed to write audit log: {e}")

    print("Workflow complete.")


def build_response(state: dict) -> dict:
    """
    Build the final JSON response. Returned exactly once.
    """
    score = state.get("score", {})
    claims = state.get("claims", [])
    verdicts = state.get("verdicts", [])

    return {
        "run_id": state.get("run_id"),
        "timestamp": state.get("timestamp"),
        "score": score,
        "details": {
            "num_prompts": len(state.get("prompts", [])),
            "num_responses": len(state.get("responses", [])),
            "num_claims": len(claims),
            "verdicts": verdicts,
        },
    }
