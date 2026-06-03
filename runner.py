import subprocess
import sys

def run_file(file_path):
    result = subprocess.run(
        ["/usr/bin/python3", str(file_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return {
            "success": True,
            "output": result.stdout + result.stderr
        }
    else:
        return {
            "success": False,
            "error": result.stdout + result.stderr
        }