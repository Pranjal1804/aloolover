from src.wrappers.bedrock import call_llm

def run_model(state: dict) -> None:
    """
    Run the LLM on generated prompts.
    Updates state["responses"].
    """
    prompts = state.get("prompts", [])
    responses = []
    
    for prompt in prompts:
        try:
            # We pass empty system message for now, or could use default system prompt from config
            response_text = call_llm(prompt)
            responses.append({"prompt": prompt, "response": response_text})
        except Exception as e:
            print(f"Error running model for prompt '{prompt[:20]}...': {e}")
            responses.append({"prompt": prompt, "response": "ERROR: " + str(e)})

    state["responses"] = responses
    print(f"Generated {len(responses)} responses.")
