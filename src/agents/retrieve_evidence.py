from src.wrappers.elasticsearch_helper import search_docs, vector_search

def retrieve_evidence(state: dict) -> None:
    """
    Retrieve evidence for extracted claims using Elasticsearch.
    Updates state["evidence"].
    """
    claims = state.get("claims", [])
    config = state.get("config", {})
    es_config = config.get("elasticsearch", {})
    index_name = es_config.get("index", "trusted_docs")
    
    evidence_list = []
    
    for claim_obj in claims:
        claim_text = claim_obj.get("text", "")
        if not claim_text:
            continue
            
        # Try retrieving evidence using text match or vector search
        # Using vector search for semantic similarity if possible
        try:
            # We default to vector search for better semantic matching
            # But might fallback to text search if vector search fails or isn't set up
            # For simplicity, let's try text search first as it is safer without embeddings set up
            # However, prompt-driven retrieval usually benefits from vector search.
            # Let's try text search first as it is simpler.
            docs = search_docs(claim_text, index=index_name)
            
            # If search_docs returns nothing, maybe try keywords?
            # Or assume search_docs uses an analyzer that handles some varying terms.
            
            # We collect top docs
            evidence_list.append({
                "claim": claim_obj,
                "documents": docs[:3] # Top 3 docs
            })
            
        except Exception as e:
            print(f"Error retrieving evidence for claim '{claim_text[:20]}...': {e}")
            # Try appending with empty docs to avoid breaking chain
            evidence_list.append({
                "claim": claim_obj,
                "documents": []
            })
            
    state["evidence"] = evidence_list
    print(f"Retrieved evidence for {len(evidence_list)} claims.")
