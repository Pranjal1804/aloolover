import os
from src.config.loader import load_config
from src.wrappers.elasticsearch_helper import index_doc, clear_index
from src.wrappers.bedrock import embed
import uuid

def run_ingest(config_path: str | None = None, clear_first: bool = False) -> dict:
    """
    Run document ingestion pipeline.
    """
    config = load_config(config_path)
    if clear_first:
        es_config = config.get("elasticsearch", {})
        index_name = es_config.get("index", "trusted_docs")
        clear_index(index_name)

    sources = config.get("doc_sources", [])
    es_config = config.get("elasticsearch", {})
    index_name = es_config.get("index", "trusted_docs")
    
    stats = {"indexed": 0, "errors": 0}
    
    for source in sources:
        source_type = source.get("type")
        source_path = source.get("path")
        
        if source_type == "file" and source_path:
             # Basic implementation: read all .txt files in directory
             if os.path.isdir(source_path):
                 for root, _, files in os.walk(source_path):
                     for file in files:
                         if file.endswith(".txt") or file.endswith(".md"):
                             file_path = os.path.join(root, file)
                             try:
                                 with open(file_path, 'r', encoding='utf-8') as f:
                                     content = f.read()
                                     
                                 # Chunking logic (simple split by paragraphs or chars)
                                 # For demo, taking whole file if small, or chunks
                                 chunks = [content] # Simplified
                                 
                                 for i, chunk in enumerate(chunks):
                                     if not chunk.strip():
                                         continue
                                         
                                     # Embed
                                     try:
                                         embedding = embed(chunk)
                                     except Exception as e:
                                         print(f"Embedding failed for {file}: {e}")
                                         # Continue without embedding? Or skip?
                                         # ES helper might require embedding for vector search
                                         # If we fail, we probably can't index properly for vector search
                                         continue
                                     
                                     doc_id = str(uuid.uuid4())
                                     doc_body = {
                                         "content": chunk,
                                         "source": file_path,
                                         "embedding": embedding
                                     }
                                     
                                     index_doc(index_name, doc_id, doc_body)
                                     stats["indexed"] += 1
                                     
                             except Exception as e:
                                 print(f"Error processing file {file_path}: {e}")
                                 stats["errors"] += 1
             else:
                 print(f"Source path {source_path} is not a directory.")
        else:
            print(f"Source type {source_type} not supported or path missing.")
            
    return stats
