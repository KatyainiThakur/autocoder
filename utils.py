from pathlib import Path

def get_file_data(file_name):
    file_path = Path(file_name)
    content = file_path.read_text(encoding="utf-8")
    return {
        "name": file_path.name,
        "content": content
    }

def parse_task_blocks(task_file):
    lines = Path(task_file).read_text(
        encoding="utf-8"
    ).splitlines()
    blocks = []
    current = None
    instructions = []
    reading_instructions = False
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line == "Task:":
            if current:
                current["instructions"] = "\n".join(
                    instructions
                ).strip()
                blocks.append(current)
            current = {
                "task": "",
                "instructions": "",
                "input": [],
                "output": "py",
                "run": "no"
            }
            instructions = []
            if i + 1 < len(lines):
                current["task"] = lines[i + 1].strip()
            reading_instructions = False
        elif line == "Instructions:":
            reading_instructions = True
        elif line == "Input:":
            reading_instructions = False
            if i + 1 < len(lines):
                input_line = lines[i + 1].strip()
                current["input"] = [
                    file.strip()
                    for file in input_line.split(",")
                    if file.strip()
                ]
        elif line == "Output:":
            reading_instructions = False
            if i + 1 < len(lines):
                current["output"] = lines[i + 1].strip().lower()
        elif line == "Run:":
            reading_instructions = False
            if i + 1 < len(lines):
                current["run"] = lines[i + 1].strip()
        elif reading_instructions:
            instructions.append(line)
        i += 1
    if current:
        current["instructions"] = "\n".join(
            instructions
        ).strip()
        blocks.append(current)
    return blocks