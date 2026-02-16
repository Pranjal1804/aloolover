import requests
import json
import subprocess
import os

def simulate_ci():
    print("🚀 Simulating GitHub Actions CI/CD Pipeline...")
    
    # 1. Trigger Evaluate
    print("Step 1: Calling /evaluate endpoint...")
    try:
        response = requests.post("http://localhost:8000/evaluate", json={"use_case": "ci_demo"})
        if response.status_code != 200:
            print(f"❌ API Error: {response.text}")
            return
        
        result = response.json()
        print(f"✅ Evaluation Complete. Decision: {result['score']['decision']}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return

    # 2. Update README using the existing script
    print("Step 2: Updating README.md status...")
    with open("temp_result.json", "w") as f:
        json.dump(result, f)
        
    try:
        # Run the script that the real GitHub Action would run
        subprocess.run(["python3", "scripts/update_readme_badge.py", json.dumps(result)], check=True)
        print("✅ README.md updated successfully.")
    except Exception as e:
        print(f"❌ Failed to update README: {e}")

    # 3. Check for deployment block
    decision = result['score']['decision']
    if decision == "reject":
        print("\n🚨 CI JOB FAILED: LLM Reliability Gate REJECTED the deployment.")
        print("Check README.md for the failure summary.")
    else:
        print("\n✨ CI JOB PASSED: LLM Reliability satisfies requirements.")

if __name__ == "__main__":
    simulate_ci()
