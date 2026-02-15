import pytest
from src.agents.score_risk import score_risk

def test_score_risk_calculation():
    # Setup state
    state = {
        "verdicts": [
            {"label": "supported"},
            {"label": "supported"},
            {"label": "weakly_supported"},
            {"label": "unsupported"}
        ],
        "config": {
            "thresholds": {"deploy": 0.8, "warn": 0.5}
        }
    }
    
    # Run agent
    score_risk(state)
    
    # Assertions
    score = state["score"]
    assert score["total_claims"] == 4
    assert score["supported"] == 2
    assert score["weakly_supported"] == 1
    assert score["unsupported"] == 1
    
    # Calculation: (2 + 0.5*1) / 4 = 2.5/4 = 0.625
    # Thresholds: deploy 0.8, warn 0.5
    # Reliability: 0.625
    # Expect decision: "warn"
    
    assert score["reliability"] == 0.625
    assert score["decision"] == "warn"

def test_score_risk_empty():
    state = {"verdicts": []}
    score_risk(state)
    score = state["score"]
    assert score["total_claims"] == 0
    assert score["decision"] == "unknown"
