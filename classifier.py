import ast

def is_valid_python(code):
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False

def detect_response_type(response):
    response = response.strip()

    if response.startswith('"') and response.endswith('"'):
        response = response[1:-1].strip()

    if response.startswith("```"):
        lines = response.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        response = "\n".join(lines).strip()

    response = response.replace("## /think", "").replace("/think", "").strip()

    lines = response.split("\n")
    lines = [l for l in lines if not (l.strip().startswith("##") and l.strip().endswith(".py"))]
    response = "\n".join(lines).strip()

    response = response.rstrip('`').strip()

    response = response.rstrip("]").strip()

    is_txt = (
        response.startswith("'''") and response.endswith("'''")
    )
    is_py = (
        response.startswith("##") and response.endswith("##")
    )

    if not is_py and response.startswith("##"):
        response = response + "\n##"
        is_py = True

    if not is_py and "##" in response:
        first = response.find("##")
        last = response.rfind("##")
        if first != last:
            response = "##" + response[first+2:last] + "##"
            is_py = True

    if is_txt:
        start = response.find("'''") + 3
        end = response.rfind("'''")
        content = response[start:end].strip().rstrip("]`)'\"`").strip()
        return {"type": "txt", "content": content}

    if is_py:
        content = response[2:-2].strip()
        if is_valid_python(content):
            return {"type": "py", "content": content}

    if "def " in response or "import " in response or "print(" in response:
        if is_valid_python(response):
            return {"type": "py", "content": response}

    return {"type": "txt", "content": response}