from pathlib import Path
import time

def create_run_folder():
    run_id = f"run_{int(time.time())}"
    run_path = Path("results") / run_id
    run_path.mkdir(parents=True, exist_ok=True)
    return run_path, run_id