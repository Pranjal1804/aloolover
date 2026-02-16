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
    CRITICAL: You must return ONLY valid JSON. No conversational text, no explanations, no headers.
    
    Instruction: Verify the following CLAIM against the provided EVIDENCE.
    Labels: 
    - "supported": Evidence directly proves the claim.
    - "weakly_supported": Evidence suggests it but isn't conclusive.
    - "unsupported": Evidence contradicts or doesn't mention the claim.
    
    EVIDENCE: {evidence_text}
    CLAIM: {claim}
    
    Output Format (JSON only): {{"label": "supported|weakly_supported|unsupported", "justification": "short explanation"}}
    """
    
    for item in evidence_list:
        claim_obj = item.get("claim", {})
        claim_text = claim_obj.get("text", "")
        documents = item.get("documents", [])
        
        if not claim_text:
            continue
            
        evidence_content = "\n\n".join([doc.get("content", "") for doc in documents])
        if not evidence_content:
            evidence_content = "No relevant evidence found."
            
        prompt = verification_prompt_template.format(claim=claim_text, evidence_text=evidence_content[:2000]) # Truncate context if needed
        
        try:
            response_json = call_llm(prompt)
            # Clean up response
            response_json = response_json.strip()
            if response_json.startswith("```json"):
                response_json = response_json[7:]
            if response_json.startswith("```"):
                response_json = response_json[3:]
            # Robust JSON extraction
            content = response_json.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                 content = content.split("```")[1].split("```")[0].strip()
            
            try:
                data = json.loads(content)
                verdicts.append({
                    "claim": claim_text,
                    "label": data.get("label", "unsupported").lower(),
                    "justification": data.get("justification", "No justification provided.")
                })
            except json.JSONDecodeError:
                print(f"Failed to parse JSON for verification: {content[:100]}...")
                verdicts.append({
                    "claim": claim_text,
                    "label": "unsupported",
                    "justification": f"Parse error on verifier response: {content[:50]}"
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
