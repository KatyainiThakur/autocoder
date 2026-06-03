from pathlib import Path
from ai import ask_qwen
from runner import run_file
from prompt import build_fix_prompt, build_test_prompt, build_test_fix_prompt
from storage import save_result
from classifier import detect_response_type


def fix_loop(
    file_path,
    run_path,
    instructions,
    timeout=600,
    max_retries=5
):
    file_path = Path(file_path)
    original_code = file_path.read_text(encoding="utf-8")
    attempts_log = []

    for attempt in range(1, max_retries + 1):
        result = run_file(file_path)

        if result["success"]:
            print(f"Success on attempt {attempt}")
            print("Output:", result["output"])
            return True, file_path, attempts_log

        error = result["error"]
        attempts_log.append({
            "attempt": attempt,
            "error": error
        })

        print(
            f"Attempt {attempt} failed:\n"
            f"{error}"
        )

        if attempt == max_retries:
            print("Max retries reached. Could not fix.")
            return False, file_path, attempts_log

        prompt = build_fix_prompt(
            original_code,
            file_path.read_text(encoding="utf-8"),
            error,
            instructions
        )
        raw = ask_qwen(prompt, timeout)
        raw = raw.rstrip('`').strip()
        parsed = detect_response_type(raw)

        if parsed["type"] != "py":
            print(f"Fix response was not python on attempt {attempt}, skipping...")
            continue

        file_path = save_result(
            parsed["content"],
            "py",
            run_path,
            f"fixed_attempt_{attempt}"
        )

    return False, file_path, attempts_log


def test_loop(
    fixed_file_path,
    run_path,
    timeout=600,
    max_retries=5
):
    fixed_file_path = Path(fixed_file_path)
    fixed_code = fixed_file_path.read_text(encoding="utf-8")
    attempts_log = []

    print("Generating test cases...")

    prompt = build_test_prompt(fixed_code)
    raw = ask_qwen(prompt, timeout)
    raw = raw.rstrip('`').strip()
    parsed = detect_response_type(raw)

    if parsed["type"] != "py":
        print("Test response was not python, skipping test loop...")
        return False, attempts_log

    test_file = save_result(
        parsed["content"],
        "py",
        run_path,
        f"{fixed_file_path.stem}_test_cases"
    )

    print("Test cases saved at:", test_file)

    for attempt in range(1, max_retries + 1):
        result = run_file(test_file)

        if result["success"]:
            print(f"✅ Tests PASSED on attempt {attempt}")
            print(result["output"])
            return True, attempts_log

        error = result["error"]
        attempts_log.append({
            "attempt": attempt,
            "error": error
        })

        print(f"❌ Tests FAILED on attempt {attempt}")
        print(f"Error:\n{error}")

        if attempt == max_retries:
            print("❌ Max test retries reached. Could not fix tests.")
            return False, attempts_log

        print(f"Sending failure to AI for fix (attempt {attempt})...")

        test_code = test_file.read_text(encoding="utf-8")
        prompt = build_test_fix_prompt(
            test_code,
            error,
            fixed_code
        )
        raw = ask_qwen(prompt, timeout)
        raw = raw.rstrip('`').strip()
        parsed = detect_response_type(raw)

        if parsed["type"] != "py":
            print("Invalid test fix response, retrying with fresh prompt...")
            prompt = build_test_prompt(fixed_code)
            raw = ask_qwen(prompt, timeout)
            raw = raw.rstrip('`').strip()
            parsed = detect_response_type(raw)
            if parsed["type"] != "py":
                print(f"Could not get valid test code on attempt {attempt}")
                continue

        test_file = save_result(
            parsed["content"],
            "py",
            run_path,
            f"{fixed_file_path.stem}_test_cases_attempt_{attempt}"
        )

        print(f"Fixed test cases saved at: {test_file}")

    return False, attempts_log