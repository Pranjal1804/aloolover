def score_risk(state: dict) -> None:
    """
    Calculate risk score based on verdicts and configuration thresholds.
    Updates state["score"].
    """
    verdicts = state.get("verdicts", [])
    if not verdicts:
        # No verdicts, can't score. Initialize/Reset score.
        state["score"] = {
            "risk": 0.0,
            "decision": "unknown",
            "total_claims": 0,
            "supported": 0,
            "weakly_supported": 0,
            "unsupported": 0
        }
        return

    # Count verdicts
    total = len(verdicts)
    supported = sum(1 for v in verdicts if v.get("label") == "supported")
    weakly_supported = sum(1 for v in verdicts if v.get("label") == "weakly_supported")
    unsupported = sum(1 for v in verdicts if v.get("label") == "unsupported")

    # Simple risk calculation: (unsupported + 0.5 * weakly_supported) / total
    # Adjust weights as needed.
    risk_score = (unsupported + 0.5 * weakly_supported) / total if total > 0 else 0.0
    
    # Get thresholds from config
    config = state.get("config", {})
    thresholds = config.get("thresholds", {"deploy": 0.8, "warn": 0.5}) # Default if missing
    
    # Decision logic
    # In this logic, lower risk score is better? 
    # Or maybe "deploy" threshold is for *confidence*?
    # Usually thresholds like 0.8 mean "80% confidence/safety required".
    # Let's assume the threshold is for SAFETY score = 1 - risk.
    # OR risk threshold: "alert if risk > 0.5".
    # Let's assume config "deploy": 0.8 means "Reliability Score > 0.8".
    # Reliability = (supported) / total ? Or (supported + 0.5*weak) / total?
    
    # Let's use a "Reliability Score" where supported=1, weak=0.5, unsupported=0.
    reliability_score = (supported + 0.5 * weakly_supported) / total if total > 0 else 0.0
    
    decision = "reject"
    if reliability_score >= thresholds.get("deploy", 0.8):
        decision = "deploy"
    elif reliability_score >= thresholds.get("warn", 0.5):
        decision = "warn"
        
    state["score"] = {
        "risk": 1.0 - reliability_score, # Risk is inverse of reliability
        "decision": decision,
        "total_claims": total,
        "supported": supported,
        "weakly_supported": weakly_supported,
        "unsupported": unsupported,
        "reliability": reliability_score # Added for clarity
    }
    
    print(f"Scored Risk: {state['score']}")
