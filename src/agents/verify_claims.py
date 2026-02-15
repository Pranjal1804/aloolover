from src.wrappers.bedrock import call_llm
import json

def verify_claims(state: dict) -> None:
    """
    Verify claims against retrieved evidence.
    Updates state["verdicts"].
    """
    evidence_list = state.get("evidence", [])
    verdicts = []
    
    verification_prompt_template = """
    Verify the following claim based on the provided evidence.
    
    Claim: {claim}
    
    Evidence:
    {evidence_text}
    
    Determine if the claim is supported by the evidence.
    Return a JSON object with:
    - "label": "supported", "weakly_supported", or "unsupported"
    - "justification": Brief explanation.
    
    Output JSON:
    """
    
    for item in evidence_list:
        claim_obj = item.get("claim", {})
        claim_text = claim_obj.get("text", "")
        documents = item.get("documents", [])
        
        if not claim_text:
            continue
            
        evidence_text = "\n\n".join([doc.get("content", "") for doc in documents])
        if not evidence_text:
            evidence_text = "No relevant evidence found."
            
        prompt = verification_prompt_template.format(claim=claim_text, evidence_text=evidence_text[:2000]) # Truncate context if needed
        
        try:
            response_json = call_llm(prompt)
            # Clean up response
            response_json = response_json.strip()
            if response_json.startswith("```json"):
                response_json = response_json[7:]
            if response_json.startswith("```"):
                response_json = response_json[3:]
            if response_json.endswith("```"):
                response_json = response_json[:-3]
                
            verdict = json.loads(response_json)
            
            verdicts.append({
                "claim": claim_text,
                "label": verdict.get("label", "unsupported"),
                "justification": verdict.get("justification", "No justification provided.")
            })
            
        except Exception as e:
            print(f"Error verifying claim '{claim_text[:20]}...': {e}")
            verdicts.append({
                "claim": claim_text,
                "label": "unsupported", 
                "justification": f"Error during verification: {e}"
            })
            
    state["verdicts"] = verdicts
    print(f"Verified {len(verdicts)} claims.")
