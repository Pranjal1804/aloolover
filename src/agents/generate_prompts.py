import random

def generate_prompts(state: dict) -> None:
    """
    Generate prompts based on prompt categories in config.
    Updates state["prompts"].
    """
    config = state.get("config", {})
    eval_config = config.get("evaluation", {})
    categories = eval_config.get("prompt_categories", ["general"])
    num_prompts = eval_config.get("num_prompts", 5)
    
    # In a real system, this might use an LLM to generate diverse prompts 
    # or fetch from a dataset.
    # For now, we'll generate simple template-based prompts.
    
    prompts = []
    
    # Simple templates for demo
    templates = {
        "factual": [
            "What is the capital of France?",
            "Explain the theory of relativity.",
            "Who wrote Hamlet?"
        ],
        "reasoning": [
            "If A is bigger than B, and B is bigger than C, is A bigger than C?",
            "Solve for x: 2x + 5 = 15.",
            "Analyze the pros and cons of remote work."
        ],
        "creative": [
            "Write a poem about a robot.",
            "Imagine a world where gravity is half as strong.",
            "Describe a color to a blind person."
        ],
        "general": [
            "Tell me a joke.",
            "How do I bake a cake?",
            "What is the weather like?"
        ]
    }
    
    generated_count = 0
    # Determine how many prompts per category (roughly)
    per_category = max(1, num_prompts // len(categories))
    
    for cat in categories:
        cat_templates = templates.get(cat, templates["general"])
        # If we need more than we have templates for, we might duplicate or format.
        # Here we just cycle through them.
        for i in range(per_category):
            if generated_count >= num_prompts:
                break
            template = cat_templates[i % len(cat_templates)]
            prompts.append(template) # In a real agent, we might vary this using LLM.
            generated_count += 1
            
    # Fill remainder if any
    while len(prompts) < num_prompts:
        prompts.append(templates["general"][0])
        
    state["prompts"] = prompts
    print(f"Generated {len(prompts)} prompts.")
