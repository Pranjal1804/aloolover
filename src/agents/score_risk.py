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
    
    # Omniscience Score (Reliability): supported=1, weak=0.5, unsupported=0.
    # Higher is better.
    omniscience_score = (supported + 0.5 * weakly_supported) / total if total > 0 else 0.0
    
    # Hallucination Score (Risk): Inverse of reliability.
    # LOWER is better.
    hallucination_score = 1.0 - omniscience_score
    
    decision = "reject"
    if omniscience_score >= thresholds.get("deploy", 0.8):
        decision = "deploy"
    elif omniscience_score >= thresholds.get("warn", 0.5):
        decision = "warn"
        
    state["score"] = {
        "risk": hallucination_score, # Mapped to 'Hallucination' in dashboard
        "decision": decision,
        "total_claims": total,
        "supported": supported,
        "weakly_supported": weakly_supported,
        "unsupported": unsupported,
        "reliability": omniscience_score 
    }
    
    print(f"Scored Hallucination: {hallucination_score:.2f} | Reliability: {omniscience_score:.2f} | Decision: {decision}")
