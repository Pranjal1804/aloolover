from elasticsearch import Elasticsearch
from src.config.loader import load_config
import os

_es_client = None

def _get_es_client():
    global _es_client
    if _es_client is None:
        config = load_config()
        host = config.get("elasticsearch", {}).get("host", "localhost")
        port = config.get("elasticsearch", {}).get("port", 9200) # Assuming default port
        # Handle authentication if needed (omitted for simplicity/local dev)
        # Using http connection
        _es_client = Elasticsearch(f"http://{host}:{port}")
    return _es_client

def index_doc(index: str, doc_id: str, body: dict) -> None:
    """
    Index a document in Elasticsearch.
    """
    client = _get_es_client()
    client.index(index=index, id=doc_id, document=body)
    # Refresh to make it searchable immediately (useful for tests/dev, maybe remove for prod)
    client.indices.refresh(index=index)

def search_docs(query: str, index: str = "trusted_docs") -> list[dict]:
    """
    Search documents using a simple text query.
    """
    client = _get_es_client()
    response = client.search(index=index, query={"match": {"content": query}})
    return [hit["_source"] for hit in response["hits"]["hits"]]

def vector_search(text: str, index: str = "trusted_docs", k: int = 5) -> list[dict]:
    """
    Search documents using vector similarity (Must be implemented with embeddings).
    This function assumes the index has a dense_vector mapping and documents have embeddings.
    
    Note: 'text' input needs to be embedded first. This wrapper accepts text and calls embed().
    Using separate Bedrock wrapper for embedding to avoid circular deps if possible, 
    but commonly this helper might just take the vector.
    However, the signature says `text: str`. So we import embed.
    """
    # Avoid circular import by importing inside function if needed, 
    # but bedrock wrapper is a sibling.
    from src.wrappers.bedrock import embed
    
    vector = embed(text)
    
    client = _get_es_client()
    
    # KNN search query for Elasticsearch 8.x+
    # Adjust query based on ES version. Assuming >= 8.0
    query = {
        "knn": {
            "field": "embedding",
            "query_vector": vector,
            "k": k,
            "num_candidates": 100
        }
    }
    
    try:
        response = client.search(index=index, body=query)
        return [hit["_source"] for hit in response["hits"]["hits"]]
    except Exception as e:
        # Fallback for older ES versions or different valid query structure
        # Script score query common for older versions
        print(f"Vector search failed (maybe index mapping missing or ES version mismatch): {e}")
        return []
