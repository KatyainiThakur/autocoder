from pathlib import Path

def save_result(content, file_type, run_path, task_name):
    if file_type == "py":
        ext = ".py"
    else:
        ext = ".txt"

    file_path = run_path / f"{task_name}{ext}"
    file_path.write_text(content, encoding="utf-8")
    return file_path