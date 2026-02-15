import os
from src.wrappers.bedrock import call_llm
from src.wrappers.ollama import call_ollama


def run_model(state: dict) -> None:
    """
    Run the LLM *under test* on generated prompts.
    Supports: ollama | bedrock (Claude as model-under-test).
    Updates state["responses"].
    """
    config = state.get("config", {})
    target = config.get("target_model", {})
    provider = target.get("provider", "ollama")
    model_id = target.get("model_id", "llama3.2")

    # Allow env override for CI (e.g. remote Ollama URL)
    ollama_base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    prompts = state.get("prompts", [])
    responses = []

    print(f"Running target model ({provider}/{model_id})...")

    for prompt in prompts:
        try:
            if provider == "ollama":
                text = call_ollama(prompt, model_id=model_id, base_url=ollama_base)
            elif provider == "bedrock":
                # Claude as model-under-test — still verified independently
                text = call_llm(prompt, model_id_override=model_id)
            else:
                text = f"ERROR: Unknown provider '{provider}'"
            responses.append({"prompt": prompt, "response": text})
        except Exception as e:
            print(f"Error on prompt '{prompt[:30]}…': {e}")
            responses.append({"prompt": prompt, "response": f"ERROR: {e}"})

    state["responses"] = responses
    print(f"Collected {len(responses)} responses.")
