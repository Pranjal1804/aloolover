from src.ingest.pipeline import run_ingest
import os

print(f"Current CWD: {os.getcwd()}")
print(f"Checking data/docs: {os.path.exists('data/docs')}")
print(f"Contents: {os.listdir('data/docs')}")

try:
    stats = run_ingest()
    print(f"Ingest stats: {stats}")
except Exception as e:
    print(f"Ingest failed: {e}")
