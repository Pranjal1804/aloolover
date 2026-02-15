from src.config.loader import load_config
try:
    config = load_config()
    print("Config loaded successfully")
    print(config.keys())
except Exception as e:
    print(f"Config load failed: {e}")
