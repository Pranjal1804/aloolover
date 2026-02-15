from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch('src.main.run_workflow')
@patch('src.main.load_config')
def test_evaluate_endpoint(mock_load_config, mock_run_workflow):
    # Mock config
    mock_load_config.return_value = {
        "use_case": "test",
        "thresholds": {"deploy": 0.8, "warn": 0.5}
    }
    
    # Mock workflow - it modifies state in place
    def side_effect(state):
        state["score"] = {"risk": 0.1, "decision": "deploy"}
        state["claims"] = [{"text": "claim1"}]
        state["verdicts"] = [{"claim": "claim1", "label": "supported"}]
        
    mock_run_workflow.side_effect = side_effect
    
    response = client.post("/evaluate", json={"use_case": "test"})
    
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert data["score"]["decision"] == "deploy"
    assert data["details"]["num_claims"] == 1
