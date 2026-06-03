from prompt import build_report_prompt
from ai import ask_qwen
from classifier import detect_response_type
from storage import save_result


def generate_report(all_task_logs, run_id, total_time, run_path, timeout):
    report_data = f"""
Run ID: {run_id}
Total Time: {total_time} seconds
Total Tasks: {len(all_task_logs)}

"""
    for log in all_task_logs:
        report_data += f"""
Task: {log["task_name"]}
Description: {log["task"]}
Input Files: {", ".join(log["input_files"])}
Output Type: {log["output_type"]}
Output File: {log["output_file"]}
Status: {log["status"]}
Time Taken: {log["time_taken"]} seconds
"""
        if log["fix_attempts"]:
            report_data += "Fix Attempts:\n"
            for a in log["fix_attempts"]:
                report_data += f'  Attempt {a["attempt"]}: {a["error"]}\n'

        if log["test_status"] != "not run":
            report_data += f"Test Status: {log['test_status']}\n"
            if log["test_attempts"]:
                report_data += "Test Attempts:\n"
                for a in log["test_attempts"]:
                    report_data += f'  Attempt {a["attempt"]}: {a["error"]}\n'

        if "error" in log:
            report_data += f"Error: {log['error']}\n"

    print("\nGenerating report...")
    report_prompt = build_report_prompt(report_data)
    raw_report = ask_qwen(report_prompt, timeout)
    parsed_report = detect_response_type(raw_report)
    report_content = parsed_report["content"]

    report_path = save_result(
        report_content,
        "txt",
        run_path,
        "report"
    )

    print("Report saved at:", report_path)