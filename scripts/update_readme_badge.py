"""
Update README.md with the latest LLM Reliability Gate status.
Called by CI after /evaluate returns.

Usage:
    python scripts/update_readme_badge.py '{"score": {...}, ...}'
"""

import json
import sys
import os
import re


def generate_badge(result: dict) -> str:
    score = result.get("score", {})
    decision = score.get("decision", "unknown")
    risk = score.get("risk", 0.0)
    reliability = score.get("reliability", 1.0 - risk)
    total = score.get("total_claims", 0)
    supported = score.get("supported", 0)
    weak = score.get("weakly_supported", 0)
    unsupported = score.get("unsupported", 0)
    run_id = result.get("run_id", "unknown")

    if decision == "deploy":
        header = "## ✅ LLM Reliability Status"
        status_line = "**Safe to Deploy**"
    elif decision == "warn":
        header = "## ⚠️ LLM Reliability Status"
        status_line = "**Warning — Review Recommended**"
    elif decision == "reject":
        header = "## 🚨 LLM Reliability Status"
        status_line = "**❌ Deployment Blocked**"
    else:
        header = "## ❓ LLM Reliability Status"
        status_line = "**Unknown**"

    badge = f"""{header}

{status_line}

| Metric | Value |
|--------|-------|
| Hallucination Risk | {risk:.2f} |
| Reliability Score | {reliability:.2f} |
| Total Claims | {total} |
| Supported | {supported} |
| Weakly Supported | {weak} |
| Unsupported | {unsupported} |
| Decision | `{decision}` |
| Run ID | `{run_id[:8]}…` |
"""
    return badge


def update_readme(badge_text: str):
    readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")

    if not os.path.exists(readme_path):
        with open(readme_path, "w") as f:
            f.write(f"# LLM Reliability Gate\n\n{badge_text}\n")
        return

    with open(readme_path, "r") as f:
        content = f.read()

    # Replace existing badge section (between markers)
    marker_start = "<!-- RELIABILITY_GATE_START -->"
    marker_end = "<!-- RELIABILITY_GATE_END -->"

    new_section = f"{marker_start}\n{badge_text}\n{marker_end}"

    if marker_start in content:
        pattern = re.escape(marker_start) + r".*?" + re.escape(marker_end)
        content = re.sub(pattern, new_section, content, flags=re.DOTALL)
    else:
        # Insert after first heading
        lines = content.split("\n")
        insert_idx = 1  # after first line
        for i, line in enumerate(lines):
            if line.startswith("# "):
                insert_idx = i + 1
                break
        lines.insert(insert_idx, f"\n{new_section}\n")
        content = "\n".join(lines)

    with open(readme_path, "w") as f:
        f.write(content)

    print(f"README.md updated with reliability status: {badge_text.splitlines()[0]}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/update_readme_badge.py '<json>'")
        sys.exit(1)

    result = json.loads(sys.argv[1])
    badge = generate_badge(result)
    update_readme(badge)
