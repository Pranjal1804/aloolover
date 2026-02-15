from src.wrappers.bedrock import call_llm
import json

def extract_claims(state: dict) -> None:
    """
    Extract factual claims from model responses.
    Updates state["claims"].
    """
    responses = state.get("responses", [])
    claims = []
    
    extraction_prompt_template = """
    Identify the main factual claims in the following text.
    Return only a JSON list of strings, where each string is a claim.
    Do not include opinions or questions.
    
    Text: {text}
    
    Output JSON:
    """
    
    for item in responses:
        response_text = item.get("response", "")
        prompt = item.get("prompt", "")
        
        if response_text.startswith("ERROR:"):
            continue
            
        extraction_prompt = extraction_prompt_template.format(text=response_text)
        
        try:
            claims_json_str = call_llm(extraction_prompt)
            # Clean up potential markdown code blocks
            claims_json_str = claims_json_str.strip()
            if claims_json_str.startswith("```json"):
                claims_json_str = claims_json_str[7:]
            if claims_json_str.startswith("```"):
                claims_json_str = claims_json_str[3:]
            if claims_json_str.endswith("```"):
                claims_json_str = claims_json_str[:-3]
                
            extracted_claims = json.loads(claims_json_str)
            
            if isinstance(extracted_claims, list):
                for claim_text in extracted_claims:
                    claims.append({
                        "text": claim_text,
                        "source_prompt": prompt,
                        "source_response": response_text
                    })
            else:
                print(f"Warning: Extracted claims not a list: {extracted_claims}")

        except Exception as e:
            print(f"Error extracting claims from response: {e}")
            
    state["claims"] = claims
    print(f"Extracted {len(claims)} claims.")
