import subprocess
import sys
import json


def ask_qwen(prompt, timeout):
    script = f"""
import ollama, json

response = ollama.chat(
    model="qwen3:1.7b",
    messages=[
        {{"role": "user", "content": {json.dumps(prompt)}}}
    ]
)

print(json.dumps(response["message"]["content"]))
"""

    try:
        result = subprocess.run(
        ["/usr/bin/python3", "-c", script],
        capture_output=True,
        text=True,
        timeout=timeout
        )

    except subprocess.TimeoutExpired:
        raise TimeoutError(
            f"AI request timed out after {timeout} seconds"
        )

    if not result.stdout.strip():
        raise ValueError(
            f"AI returned no output. stderr: {result.stderr}"
        )

    output = result.stdout.strip()

    try:
        return json.loads(output)

    except json.JSONDecodeError:
        return output