import streamlit as st
import requests
import json
import yaml
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Claude vs Claude Reliability Dashboard", layout="wide")

st.title("🛡️ LLM Reliability Gate Dashboard")
st.markdown("Side-by-side hallucination risk comparison: **Claude 3 Haiku** vs **Claude 4.5 Haiku**")

# Sidebar - Configuration
st.sidebar.header("Settings")

# Allow user to upload documentation links or files
st.sidebar.subheader("1. Setup Documentation")
doc_files = st.sidebar.file_uploader("Upload trusted documentation (.txt, .md)", accept_multiple_files=True)

# Feature: Reset Documentation Store
clear_first = st.sidebar.checkbox("Reset Data Store (Remove old files)", value=True)

if st.sidebar.button("Ingest Documents"):
    if doc_files:
        # Save files to data/docs
        os.makedirs("data/docs", exist_ok=True)
        # If clear_first, we physically delete files in data/docs too?
        # Actually, let's just clear the dir if clear_first is true to be clean.
        if clear_first:
            for f_old in os.listdir("data/docs"):
                os.remove(os.path.join("data/docs", f_old))
        
        for f in doc_files:
            with open(os.path.join("data/docs", f.name), "wb") as buffer:
                buffer.write(f.getvalue())
        
        try:
            resp = requests.post(f"http://localhost:8000/ingest?clear_first={str(clear_first).lower()}")
            if resp.status_code == 200:
                st.sidebar.success(f"Ingested {len(doc_files)} files! (Store Reset: {clear_first})")
            else:
                st.sidebar.error(f"Ingest failed: {resp.text}")
        except Exception as e:
            st.sidebar.error(f"Connection error: {e}")
    else:
        st.sidebar.warning("Please upload files first.")

st.sidebar.subheader("2. Run Evaluation")

# Models for comparison
model_a_id = "anthropic.claude-3-haiku-20240307-v1:0"
model_b_id = "global.anthropic.claude-haiku-4-5-20251001-v1:0"

st.sidebar.info(f"Comparing:\n1. Claude 3 Haiku\n2. Claude 4.5 Haiku")

def run_eval(target_provider, target_model_id, run_name):
    config_path = ".llm-reliability.yaml"
    if not os.path.exists(config_path):
        config_path = "config.yaml"
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    config["target_model"]["provider"] = target_provider
    config["target_model"]["model_id"] = target_model_id
    
    temp_config = f"temp_config_{run_name}.yaml"
    with open(temp_config, "w") as f:
        yaml.dump(config, f)
    
    try:
        resp = requests.post("http://localhost:8000/evaluate", json={"config_path": os.path.abspath(temp_config)})
        if os.path.exists(temp_config):
            os.remove(temp_config)
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error(f"Run failed ({run_name}): {resp.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

if st.sidebar.button("Run Side-by-Side Comparison"):
    col1, col2 = st.columns(2)
    
    with st.spinner("Evaluating Model A (Claude 3 Haiku)..."):
        res_a = run_eval("bedrock", model_a_id, "claude_3")
    
    with st.spinner("Evaluating Model B (Claude 4.5 Haiku)..."):
        res_b = run_eval("bedrock", model_b_id, "claude_4_5")
        
    if res_a and res_b:
        st.subheader("📊 Comparison Table")
        
        metrics = ["Total Claims", "Supported", "Weakly Supported", "Unsupported", "Hallucination", "Decision"]
        
        data = {
            "Metric": metrics,
            "Claude 3 Haiku": [
                res_a["score"].get("total_claims", 0),
                res_a["score"].get("supported", 0),
                res_a["score"].get("weakly_supported", 0),
                res_a["score"].get("unsupported", 0),
                res_a["score"].get("risk", 0.0),
                res_a["score"].get("decision", "unknown").upper()
            ],
            "Claude 4.5 Haiku": [
                res_b["score"].get("total_claims", 0),
                res_b["score"].get("supported", 0),
                res_b["score"].get("weakly_supported", 0),
                res_b["score"].get("unsupported", 0),
                res_b["score"].get("risk", 0.0),
                res_b["score"].get("decision", "unknown").upper()
            ]
        }
        df = pd.DataFrame(data)
        # FORCE everything to string to avoid PyArrow being too smart/broken
        df = df.astype(str)
        st.table(df)
        
        # Details Columns
        c1, c2 = st.columns(2)
        with c1:
            st.header("☁️ Claude 3 Haiku Details")
            for v in res_a["details"]["verdicts"]:
                with st.expander(f"Claim: {v['claim'][:60]}..."):
                    st.write(f"**Verdict:** {v['label']}")
                    st.write(f"**Justification:** {v['justification']}")
                    
        with c2:
            st.header("✨ Claude 4.5 Haiku Details")
            for v in res_b["details"]["verdicts"]:
                with st.expander(f"Claim: {v['claim'][:60]}..."):
                    st.write(f"**Verdict:** {v['label']}")
                    st.write(f"**Justification:** {v['justification']}")
    else:
        st.error("Could not complete comparison.")

st.info("Ensure the FastAPI backend is running (`uvicorn src.main:app`) and Docker ES is up.")
