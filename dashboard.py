import streamlit as st
import requests
import json
import yaml
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="LLM Reliability Dashboard", layout="wide")

st.title("🛡️ LLM Reliability Gate Dashboard")
st.markdown("Side-by-side hallucination risk comparison: **Ollama** vs **Claude**")

# Sidebar - Configuration
st.sidebar.header("Settings")

# Allow user to upload documentation links or files
st.sidebar.subheader("1. Setup Documentation")
doc_files = st.sidebar.file_uploader("Upload trusted documentation (.txt, .md)", accept_multiple_files=True)

if st.sidebar.button("Ingest Documents"):
    if doc_files:
        # Save files to data/docs
        os.makedirs("data/docs", exist_ok=True)
        for f in doc_files:
            with open(os.path.join("data/docs", f.name), "wb") as buffer:
                buffer.write(f.getvalue())
        
        try:
            resp = requests.post("http://localhost:8000/ingest")
            if resp.status_code == 200:
                st.sidebar.success(f"Ingested {len(doc_files)} files!")
            else:
                st.sidebar.error(f"Ingest failed: {resp.text}")
        except Exception as e:
            st.sidebar.error(f"Connection error: {e}")
    else:
        st.sidebar.warning("Please upload files first.")

st.sidebar.subheader("2. Run Evaluation")
config_file = st.sidebar.file_uploader("Upload .llm-reliability.yaml (optional)", type=["yaml", "yml"])

def run_eval(target_provider, target_model_id):
    # Load base config
    config_path = ".llm-reliability.yaml"
    if not os.path.exists(config_path):
        config_path = "config.yaml"
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Override target model
    config["target_model"]["provider"] = target_provider
    config["target_model"]["model_id"] = target_model_id
    
    # Save temporary config for the run
    temp_config = f"temp_config_{target_provider}.yaml"
    with open(temp_config, "w") as f:
        yaml.dump(config, f)
    
    try:
        resp = requests.post("http://localhost:8000/evaluate", json={"config_path": os.path.abspath(temp_config)})
        os.remove(temp_config)
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error(f"Run failed ({target_provider}): {resp.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

if st.sidebar.button("Run Side-by-Side Comparison"):
    col1, col2 = st.columns(2)
    
    with st.spinner("Evaluating Model A (Ollama)..."):
        res_a = run_eval("ollama", "llama3.2")
    
    with st.spinner("Evaluating Model B (Claude)..."):
        res_b = run_eval("bedrock", "anthropic.claude-3-haiku-20240307-v1:0")
        
    if res_a and res_b:
        # Comparison Table
        st.subheader("📊 Comparison Table")
        
        metrics = ["Total Claims", "Supported", "Weakly Supported", "Unsupported", "Hallucination Risk", "Decision"]
        data = {
            "Metric": metrics,
            "Model A (Ollama)": [
                res_a["score"]["total_claims"],
                res_a["score"]["supported"],
                res_a["score"]["weakly_supported"],
                res_a["score"]["unsupported"],
                f"{res_a['score']['risk']:.2f}",
                res_a["score"]["decision"].upper()
            ],
            "Model B (Claude)": [
                res_b["score"]["total_claims"],
                res_b["score"]["supported"],
                res_b["score"]["weakly_supported"],
                res_b["score"]["unsupported"],
                f"{res_b['score']['risk']:.2f}",
                res_b["score"]["decision"].upper()
            ]
        }
        st.table(pd.DataFrame(data))
        
        # Details Columns
        c1, c2 = st.columns(2)
        
        with c1:
            st.header("🦙 Ollama Details")
            for v in res_a["details"]["verdicts"]:
                with st.expander(f"Claim: {v['claim'][:60]}..."):
                    st.write(f"**Verdict:** {v['label']}")
                    st.write(f"**Justification:** {v['justification']}")
                    
        with c2:
            st.header("☁️ Claude Details")
            for v in res_b["details"]["verdicts"]:
                with st.expander(f"Claim: {v['claim'][:60]}..."):
                    st.write(f"**Verdict:** {v['label']}")
                    st.write(f"**Justification:** {v['justification']}")
    else:
        st.error("Could not complete comparison.")

st.info("Ensure the FastAPI backend is running (`uvicorn src.main:app`) and Docker ES is up.")
