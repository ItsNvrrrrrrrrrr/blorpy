# a compiler for blor code language
# This is a compiler for the blor language, which is a simple language that is a subset of python
# The compiler is written in python, and compiles the bloc code to python code
# The compiler is written in a simple way, to make it easy to understand


import re
import sys

def blor_to_python(blor_code):
    python_code = []
    stored_content = ""  # Variable to store content from outp.println
    for line in blor_code.splitlines():
        line = line.strip()
        match = re.match(r'^outp\.println\((.*?)\)$', line)
        if match:
            stored_content = match.group(1).strip()
            python_code.append(f"blor_content = {stored_content}")
            python_code.append("print(blor_content)")  # Ensure print statement is added immediately
        elif line == "outp.print()":
            python_code.append("print(blor_content)")
        elif re.match(r'^[a-zA-Z_][a-zA-Z0-9_]* = .*', line):
            python_code.append(line)
        elif re.match(r'^if .*:', line):
            python_code.append(line)
        elif re.match(r'^[ ]{4}.*', line):  # Check for 4-space indent
            python_code.append(line)
        else:
            raise SyntaxError(f"Unsupported syntax: {line}")
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
        exec(python_code)
    except SyntaxError as e:
        print(f"Syntax Error: {e}")

if __name__ == "__main__":
    main()
