import yaml
import os
from typing import Dict, Any

def load_config(path: str | None = None) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.
    
    Args:
        path (str | None): Path to the configuration file. If None, defaults to 'config.yaml' in the current directory.
        
    Returns:
        dict: The configuration dictionary.
    """
    if path is None:
        # Default to config.yaml in the project root
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path = os.path.join(base_dir, "config.yaml")

    if not os.path.exists(path):
        raise FileNotFoundError(f"Configuration file not found at: {path}")

    with open(path, 'r') as f:
        config = yaml.safe_load(f)
        
    # Validate required keys (basic validation based on the spec)
    required_keys = ["use_case", "thresholds", "evaluation", "model", "elasticsearch", "doc_sources"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")
            
    return config
