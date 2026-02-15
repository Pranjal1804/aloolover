import yaml
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


def load_config(path: str | None = None) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.
    Searches for .llm-reliability.yaml first, then config.yaml.
    """
    if path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # Prefer .llm-reliability.yaml (the canonical name per spec)
        candidates = [
            os.path.join(base_dir, ".llm-reliability.yaml"),
            os.path.join(base_dir, "config.yaml"),
        ]
        path = None
        for c in candidates:
            if os.path.exists(c):
                path = c
                break
        if path is None:
            raise FileNotFoundError(
                f"No config file found. Searched: {candidates}"
            )

    if not os.path.exists(path):
        raise FileNotFoundError(f"Configuration file not found at: {path}")

    with open(path, "r") as f:
        config = yaml.safe_load(f)

    required_keys = [
        "use_case",
        "thresholds",
        "evaluation",
        "target_model",
        "verification_model",
        "elasticsearch",
        "doc_sources",
    ]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")

    return config
