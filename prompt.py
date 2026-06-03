def build_instructions_prompt(task, file_contents=""):
    prompt = f"""
You are a coding assistant. A user has given you a task.
Your job is to write clear and strict instructions for how to complete this task.

Task:
{task}
"""
    if file_contents:
        prompt += f"""
The following files are provided as input to work with:
{file_contents}
Do not create or recreate these files.
Do not use os.makedirs or any file creation methods.
These files already exist and are provided as input only.
"""
    prompt += """
Write detailed and strict instructions for completing this task.
The instructions will be used by an AI to complete the task.
Each instruction must be on a new line starting with *
Be very specific and strict
Cover every edge case
Do not write any code
Do not write any explanation
Do not include instructions to create or recreate input files
Do not include instructions to use os module for file creation
Just write the instructions for the task itself
Do not include instructions to add docstrings
Do not include instructions to add comments
Do not include instructions to add summaries
Return ONLY in this format:
'''your instructions here'''
Nothing before ''' and nothing after '''.
"""
    return prompt.strip()


def build_prompt(task_data, all_files, previous_output=""):
    prompt = f"""
Task:
{task_data["task"]}

Instructions:
{task_data["instructions"]}
"""
    for file_data in all_files:
        prompt += f"""
File Name:
{file_data["name"]}

Code:
{file_data["content"]}
"""
    if previous_output:
        prompt += f"""
Previous Output:
{previous_output}
"""
    if task_data["output"] == "txt":
        prompt += """
Return ONLY in this format:
'''your output here'''
Nothing before ''' and nothing after '''.

Rules:
- Plain text only
- No markdown
- No bold text
- No bullet points
- No dashes
- No headings
- No special characters
- No backticks
- Do not use ''' anywhere in the output
- Do not use quotes of any kind
- Write in simple plain sentences only
"""

    else:
        prompt += """
Start your response with ##
Write the Python code
End your response with ##

Rules:
- Start with ## and nothing before it
- End with ## and nothing after it
- No explanation
- No comments unless already in the original code
- No docstrings
- No markdown
- No headings
- No extra text before or after ##
- Only executable Python code between ##
- Do not use os.makedirs
- Do not use os.path
- Do not create or open or write to any files
- Do not import os
- Do not recreate input files
- Only write code that solves the task
- Do not add docstrings
- Do not add any comments
- Do not add any summary
"""
    return prompt


def build_fix_prompt(code, error, instructions):
    return f"""
Fix ALL errors in this Python code.

Code:
{code}

Error:
{error}

Rules:
- Fix every syntax error
- Fix every indentation error
- Fix every runtime error
- Fix every typo in function names
- Fix missing colons after function definitions
- Fix missing commas in function calls
- Do not remove any code
- Do not rewrite any code
- Do not restructure any code
- Do not add new logic
- Do not add docstrings
- Do not add comments
- Do not add type checking
- Do not add error handling unless it was already there
- Do not use os.makedirs
- Do not create or open or write to any files
- Do not import os
- Do not add any validation or type checking unless it was already in the original code
- Do not add any comments
- Do not add ## at the end of the code
- Do not add any text after the last line of code
- The closing ## is only the response wrapper not part of the code
- Keep the code exactly as it is except for the errors
- Return the complete fixed file
- Do not change any values or numbers in the code
- Do not add or remove negative signs from numbers
- Do not interpret or assume what the values should be
- Only fix syntax errors exactly as they are
- A missing comma between two numbers means add only the comma nothing else

Start your response with ##
Write only the fixed Python code
End your response with ##
""".strip()


def build_test_prompt(code):
    return f"""
Write Python unittest for this code.

Code:
{code}

Start your response with ##
Write exactly in this order:
1. import unittest
2. the original code
3. the test class
4. if __name__ == "__main__": unittest.main()
End your response with ##

Rules:
- First line must be: import unittest
- Include the original code after the import
- Remove any print statements or script level calls from the original code
- Every test method must have at least one assert statement
- Use self.assertEqual for return value checks
- Use self.assertRaises for exception checks
- Do not leave any test method empty
- Do not use markdown
- Do not use backticks
- Use real function names and real values from the code
""".strip()


def build_test_fix_prompt(test_code, error, original_code):
    return f"""
Fix this Python unittest file.

Original Code:
{original_code}

Test Code:
{test_code}

Error:
{error}

Start your response with ##
Write the fixed test code
End your response with ##

Rules:
- Fix only the test file
- Include the original code at the top
- Use unittest module
- Do not use markdown
- Do not use backticks
- Do not write placeholder text
""".strip()


def build_report_prompt(report_data):
    return f"""
Write a detailed report for this automated coding pipeline run.

Data:
{report_data}

Return ONLY in this format:
'''your report here'''
Nothing before ''' and nothing after '''.

Rules:
- Write in plain english
- Include all details from the data
- For each task include task name, input files, output file, time taken, status
- For each fix attempt include attempt number and error
- For each test attempt include attempt number and error
- Include total run time at the end
- Include overall status at the end
- No markdown
- No headings with special characters
- Plain text only
""".strip()