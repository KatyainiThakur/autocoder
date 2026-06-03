import time
from utils import get_file_data, parse_task_blocks
from prompt import build_prompt, build_instructions_prompt
from ai import ask_qwen
from classifier import detect_response_type
from storage import save_result
from run_manager import create_run_folder
from fixer import fix_loop, test_loop
from reporter import generate_report


def clean_ai_output(text):
    text = text.strip()
    if text.startswith("##python code here##"):
        text = text.replace(
            "##python code here##",
            "",
            1
        ).strip()
    return text


timeout = 600

if __name__ == "__main__":
    run_path, run_id = create_run_folder()
    task_blocks = parse_task_blocks("task.txt")
    task_counter = 1
    previous_output = ""
    all_task_logs = []
    run_start = time.time()

    for block in task_blocks:
        task_name = f"task{task_counter}"
        task_log = {
            "task_name": task_name,
            "task": block["task"].strip(),
            "input_files": block["input"],
            "output_type": block.get("output", "py").strip().lower(),
            "run": block.get("run", "no").strip().lower(),
            "status": "failed",
            "output_file": None,
            "instructions_file": None,
            "time_taken": None,
            "fix_attempts": [],
            "test_attempts": [],
            "test_status": "not run"
        }
        task_start = time.time()

        try:
            all_files = []
            for file_name in block["input"]:
                file_data = get_file_data(file_name)
                all_files.append(file_data)

            # build file contents string for instructions prompt
            file_contents = ""
            for file_data in all_files:
                file_contents += f"""
File Name:
{file_data["name"]}

Code:
{file_data["content"]}
"""

            # if no instructions in task, ask AI to generate them
            if not block["instructions"].strip():
                print(f"Generating instructions for {task_name}...")
                instructions_prompt = build_instructions_prompt(
                    block["task"].strip(),
                    file_contents.strip()
                )
                raw_instructions = ask_qwen(instructions_prompt, timeout)
                parsed_instructions = detect_response_type(raw_instructions)
                instructions = parsed_instructions["content"]

                instructions_file = save_result(
                    instructions,
                    "txt",
                    run_path,
                    f"{task_name}_instructions"
                )
                task_log["instructions_file"] = str(instructions_file)
                print(f"Instructions saved at: {instructions_file}")
            else:
                instructions = block["instructions"].strip()
                task_log["instructions_file"] = "provided in task.txt"

            task_data = {
                "task": block["task"].strip(),
                "instructions": instructions,
                "output": block.get("output", "py").strip().lower()
            }

            prompt = build_prompt(
                task_data,
                all_files,
                previous_output
            )

            raw_content = ask_qwen(prompt, timeout)
            raw_content = clean_ai_output(raw_content)
            result = detect_response_type(raw_content)

            file_type = result["type"]
            content = result["content"]

            saved_path = save_result(
                content,
                file_type,
                run_path,
                task_name
            )

            task_log["output_file"] = str(saved_path)
            task_log["status"] = "success"

            print(f"{task_name} saved at:", saved_path)
            previous_output = raw_content

            if block.get("run", "").strip().lower() == "yes" and file_type == "py":
                success, fixed_path, fix_attempts = fix_loop(
                    saved_path,
                    run_path,
                    task_data["instructions"],
                    timeout=timeout,
                    max_retries=5
                )
                task_log["fix_attempts"] = fix_attempts
                task_log["status"] = "success" if success else "failed"

                if success:
                    test_success, test_attempts = test_loop(
                        fixed_path,
                        run_path,
                        timeout=timeout,
                        max_retries=5
                    )
                    task_log["test_attempts"] = test_attempts
                    task_log["test_status"] = "passed" if test_success else "failed"

        except Exception as e:
            print(f"[ERROR] {task_name} failed:", str(e))
            task_log["status"] = "failed"
            task_log["error"] = str(e)

        task_log["time_taken"] = round(time.time() - task_start, 2)
        all_task_logs.append(task_log)
        task_counter += 1

    total_time = round(time.time() - run_start, 2)
    generate_report(all_task_logs, run_id, total_time, run_path, timeout)

    print("\nRun Completed:", run_id)