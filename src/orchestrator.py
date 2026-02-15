from src.agents.score_risk import score_risk
from src.agents.generate_prompts import generate_prompts
from src.agents.run_model import run_model
from src.agents.extract_claims import extract_claims
from src.agents.retrieve_evidence import retrieve_evidence
from src.agents.verify_claims import verify_claims

def run_workflow(state: dict) -> None:
    """
    Run the complete evaluation workflow.
    Updates state in-place.
    """
    # 1. Generate Prompts
    print("Step 1: Generating Prompts...")
    generate_prompts(state)
    
    # 2. Run Model
    print("Step 2: Running Model...")
    run_model(state)
    
    # 3. Extract Claims
    print("Step 3: Extracting Claims...")
    extract_claims(state)
    
    # 4. Retrieve Evidence
    print("Step 4: Retrieve Evidence...")
    retrieve_evidence(state)
    
    # 5. Verify Claims
    print("Step 5: Verifying Claims...")
    verify_claims(state)
    
    # 6. Score Risk
    print("Step 6: Scoring Risk...")
    score_risk(state)
    
    print("Workflow complete.")

def build_response(state: dict) -> dict:
    """
    Construct the final response object from the workflow state.
    """
    score = state.get("score", {})
    claims = state.get("claims", [])
    verdicts = state.get("verdicts", [])
    
    # Enhance verdicts with context if needed
    # (Here we just return what's in state, potentially filtering sensitive info)
    
    return {
        "score": score,
        "details": {
            "num_claims": len(claims),
            "verdicts": verdicts
        }
    }
