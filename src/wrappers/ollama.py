import requests


def call_ollama(prompt: str, model_id: str = "llama3.2", system: str = "",
                base_url: str = "http://localhost:11434") -> str:
    """
    Call a local (or remote) Ollama instance.
    base_url can be overridden via OLLAMA_BASE_URL env var for CI.
    """
    url = f"{base_url}/api/generate"

    payload = {
        "model": model_id,
        "prompt": prompt,
        "system": system,
        "stream": False,
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.RequestException as e:
        print(f"Ollama error: {e}")
        return f"ERROR: Ollama call failed: {e}"
