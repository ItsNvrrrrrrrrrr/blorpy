# a compiler for blor code language
# This is a compiler for the blor language, which is a simple language that is a subset of python
# The compiler is written in python, and compiles the bloc code to python code
# The compiler is written in a simple way, to make it easy to understand


import re
import sys

def clean_condition(cond):
    # Replace double-quoted numbers with unquoted numbers for numeric comparisons.
    return re.sub(r'"(\d+)"', r'\1', cond)

def translate_line(line, stored):
    # Translate a single line (without braces) into one or more Python lines.
    # Returns a tuple (translated_lines, new_stored) where new_stored may update stored_content.
    lines_out = []
    m = re.match(r'^outp\.println\((.*?)\)$', line)
    if m:
        stored = m.group(1).strip()
        lines_out.append(f"blor_content = {stored}")
        lines_out.append("print(blor_content)")
    elif line == "outp.print()":
        lines_out.append("print(blor_content)")
    # Handle int.age.input: attempt conversion, fallback to 0 on failure.
    elif re.match(r'^int\.age\.input\((.*?)\)$', line):
        m = re.match(r'^int\.age\.input\((.*?)\)$', line)
        input_prompt = m.group(1).strip()
        lines_out.append("try:")
        lines_out.append(f"    age = int(input({input_prompt}))")
        lines_out.append("except ValueError:")
        lines_out.append("    print('Invalid input for age')")
        lines_out.append("    age = 0")
    # Handle plain age.input, keeping the input as a string.
    elif re.match(r'^age\.input\((.*?)\)$', line):
        m = re.match(r'^age\.input\((.*?)\)$', line)
        input_prompt = m.group(1).strip()
        lines_out.append(f"age = input({input_prompt})")
    elif re.match(r'^while\.loop\((.*?)\)$', line):
        m = re.match(r'^while\.loop\((.*?)\)$', line)
        condition = clean_condition(m.group(1).strip())
        lines_out.append(f"while {condition}:")
    elif re.match(r'^else if (.*)$', line):
        m = re.match(r'^else if (.*)$', line)
        condition = clean_condition(m.group(1).strip())
        lines_out.append(f"elif {condition}:")
    elif re.match(r'^if (.*)$', line):
        m = re.match(r'^if (.*)$', line)
        condition = clean_condition(m.group(1).strip())
        lines_out.append(f"if {condition}:")
    elif re.match(r'^else$', line):
        lines_out.append("else:")
    elif re.match(r'^[a-zA-Z_][a-zA-Z0-9_]* = .*', line):
        lines_out.append(line)
    # Support 4-space indented lines pass-through (e.g. for inner content)
    elif re.match(r'^[ ]{4}.*', line):
        lines_out.append(line)
    else:
        raise SyntaxError(f"Unsupported syntax: {line}")
    return lines_out, stored

def blor_to_python(blor_code):
    python_code = []
    indent = 0
    stored_content = ""
    for orig in blor_code.splitlines():
        raw_line = orig.rstrip()
        if not raw_line.strip():
            continue
        line = raw_line.strip()
        # Skip comment lines
        if line.startswith("//"):
            continue
        # Decrease indent for leading closing braces
        while line.startswith("}"):
            indent = max(indent - 1, 0)
            line = line[1:].strip()
        increase = False
        if line.endswith("{"):
            increase = True
            line = line[:-1].strip()
        line = line.replace("{", "").replace("}", "").strip()
        if not line:
            continue
        try:
            trans_lines, stored_content = translate_line(line, stored_content)
        except SyntaxError as e:
            raise SyntaxError(e)
        for t in trans_lines:
            python_code.append("    " * indent + t)
        if increase:
            indent += 1
    return "\n".join(python_code)

def main():
    if len(sys.argv) < 2:
        print("Usage: python blorc_compiler.py <source.or>")
        return
    if not sys.argv[1].endswith(".or"):
        print("Error: Only .or files are supported.")
        return
    with open(sys.argv[1], "r") as file:
        blor_code = file.read()
    try:
        python_code = blor_to_python(blor_code)
        # Uncomment the next line to debug the generated Python code:
        # print("Generated Python code:\n", python_code)
        exec(python_code)
    except SyntaxError as e:
        print(f"Syntax Error: {e}")

if __name__ == "__main__":
    main()
