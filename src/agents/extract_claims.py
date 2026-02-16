from src.wrappers.bedrock import call_llm
import json
import uuid

def extract_claims(state: dict) -> None:
    """
    Extract factual claims from model responses.
    Updates state["claims"].
    """
    responses = state.get("responses", [])
    claims = []
    
    extraction_prompt_template = """
    Identify the main factual claims in the following text.
    Return ONLY a JSON list of strings, where each string is a claim.
    If the text is empty, irrelevant, or contains no factual claims, return an empty list [].
    Do not include explanations, intro, or markdown.
    
    Text: {text}
    
    Output JSON: []
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
            claims_llm_response = call_llm(extraction_prompt)
            
            # Robust JSON extraction
            content_to_parse = claims_llm_response.strip()
            if "```json" in content_to_parse:
                content_to_parse = content_to_parse.split("```json")[1].split("```")[0].strip()
            elif "```" in content_to_parse:
                 content_to_parse = content_to_parse.split("```")[1].split("```")[0].strip()
            
            try:
                extracted_data = json.loads(content_to_parse)
                # Assuming the LLM is instructed to return a list of strings directly,
                # or a dictionary with a "claims" key containing a list.
                # Adjusting based on the original code's expectation of a list.
                if isinstance(extracted_data, list):
                    item_claims = extracted_data
                elif isinstance(extracted_data, dict) and "claims" in extracted_data:
                    item_claims = extracted_data["claims"]
                else:
                    item_claims = []
                    print(f"Warning: Extracted data not a list or dict with 'claims' key: {extracted_data}")

                for c in item_claims:
                    if isinstance(c, str): # Ensure the claim itself is a string
                        claims.append({
                            "id": str(uuid.uuid4()),
                            "text": c, # Changed 'claim' to 'text' to match original structure
                            "source_prompt": prompt, # Changed 'r["prompt"]' to 'prompt'
                            "source_response": response_text # Changed 'r["response"]' to 'response_text'
                        })
                    else:
                        print(f"Warning: Claim item is not a string: {c}")
            except json.JSONDecodeError:
                print(f"Failed to parse JSON for claims: {content_to_parse[:100]}...")

        except Exception as e:
            print(f"Error extracting claims from response: {e}")
            
    state["claims"] = claims
    print(f"Extracted {len(claims)} claims.")
