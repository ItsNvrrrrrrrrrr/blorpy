# blor compiler based by python , Rewis and Wren
# This is a compiler for the blor language, which is a simple language that is a subset of python
# The compiler is written in python, and compiles the bloc code to python code
# The compiler is written in a simple way, to make it easy to understand


import re
import sys

def clean_condition(cond):
    # Replace double-quoted numbers with unquoted numbers for numeric comparisons.
    cond = re.sub(r'"(\d+)"', r'\1', cond)
    # Replace single '=' with '==' for equality in conditions
    cond = re.sub(r'(?<![=!<>])=(?![=])', '==', cond)
    # New: Wrap bare identifiers in equality comparisons with quotes.
    cond = re.sub(r'==\s*([a-zA-Z_]\w*)\b', r"== '\1'", cond)
    return cond

def process_println_expr(expr):
    # Tokenize the expression by the '+' operator.
    tokens = [t.strip() for t in expr.split('+')]
    parts = []
    for token in tokens:
        if token.startswith('"') and token.endswith('"'):
            # For string literals, remove quotes and escape any braces.
            parts.append(token[1:-1].replace("{", "{{").replace("}", "}}"))
        else:
            # For variables, simply wrap them in curly braces for direct interpolation.
            parts.append(f"{{{token}}}")
    # Build and return the final f-string.
    return f'f"{ "".join(parts) }"'

def translate_line(line, stored):
    # New: Check for common typos in every command.
    typo_map = {
        "st.": "str.",
        "it.": "int.",
        "oup.println": "outp.println",
        "oup.print": "outp.print",
        "publc": "public",
        "privte": "private",
        "functon": "function",
        "funcion": "function"
        # Extend with more common typos as needed.
    }
    for typo, correction in typo_map.items():
        if typo in line:
            suggested = line.replace(typo, correction)
            raise SyntaxError(f"Unsupported syntax '{line}'. Did you mean '{suggested}'?")

    lines_out = []
    # Updated: Use regex to match outp.println() patterns.
    m = re.match(r'^outp\.println\((.*)\)$', line)
    if m:
        expr = m.group(1).strip()
        if (',' in expr or '+' in expr):
            processed_expr = process_println_expr(expr)
            line_out = f"print({processed_expr})"
        else:
            line_out = f"print({expr})"
        return [line_out], stored
    elif line == "outp.print()":
        lines_out = ["print(blor_content)"]
    # New: support generic variable input for int and str (e.g. int.yourAge.input("..."), str.yourName.input("..."))
    m = re.match(r'^(int|str)\.([a-zA-Z_]\w*)\.input\((.*?)\)$', line)
    if m:
        typ = m.group(1)
        var_name = m.group(2)
        input_prompt = m.group(3).strip()
        if typ == "int":
            lines_out = [
                "try:",
                f"    {var_name} = int(input({input_prompt}))",
                "except ValueError:",
                f"    print('Invalid input for {var_name}')",
                f"    {var_name} = 0"
            ]
        else:
            lines_out = [f"{var_name} = input({input_prompt})"]
        return lines_out, stored
    elif re.match(r'^while\.loop\((.*?)\)$', line):
        m = re.match(r'^while\.loop\((.*?)\)$', line)
        condition = clean_condition(m.group(1).strip())
        lines_out = [f"while {condition}:"]
    elif re.match(r'^else if (.*)$', line):
        m = re.match(r'^else if (.*)$', line)
        condition = clean_condition(m.group(1).strip())
        lines_out = [f"elif {condition}:"]
    elif re.match(r'^if (.*)$', line):
        m = re.match(r'^if (.*)$', line)
        condition = clean_condition(m.group(1).strip())
        lines_out = [f"if {condition}:"]
    elif line == "else":
        lines_out = ["else:"]
    # New: support private main function without a name.
    elif line == "private main function()":
        lines_out = ["if __name__ == '__main__':"]
    # Updated: support function definitions with parameters.
    elif re.match(r'^(public new|private main)\s+function\s+(\w+)\s*\((.*?)\)\s*$', line):
        m = re.match(r'^(public new|private main)\s+function\s+(\w+)\s*\((.*?)\)\s*$', line)
        func_name = m.group(2)
        params_list = m.group(3).strip()
        if params_list:
            # Split by comma and remove type prefixes (e.g. "str." or "int.").
            params = [p.strip().split('.')[-1] for p in params_list.split(',')]
            params_str = ", ".join(params)
        else:
            params_str = ""
        lines_out = [f"def {func_name}({params_str}):"]
    # Updated: support function calls with optional arguments.
    elif re.match(r'^function\.(\w+)\((.*?)\)$', line):
        m = re.match(r'^function\.(\w+)\((.*?)\)$', line)
        func_name = m.group(1)
        args = m.group(2).strip()
        lines_out = [f"{func_name}({args})"]
    # New: support 'break'
    elif line == "break":
        lines_out = ["break"]
    elif re.match(r'^[a-zA-Z_][a-zA-Z0-9_]* = .*', line):
        lines_out = [line]
    # Support 4-space indented lines pass-through (e.g. for inner content)
    elif re.match(r'^[ ]{4}.*', line):
        lines_out = [line]
    else:
        # Enhanced error message for unsupported syntax.
        raise SyntaxError(f"Unsupported syntax in line: '{line}'. Please verify your Blor syntax.")
    return lines_out, stored

def blor_to_python(blor_code):
    python_code = []
    errors = []  # New: collect errors from all lines.
    indent = 0
    stored_content = ""
    # Add line numbering to improve error reporting.
    for idx, orig in enumerate(blor_code.splitlines(), start=1):
        raw_line = orig.rstrip('\n')
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
            for t in trans_lines:
                python_code.append("    " * indent + t)
            if increase:
                indent += 1
        except SyntaxError as e:
            offset = len(orig) - len(orig.lstrip())
            pointer_line = " " * offset + "^"
            error_msg = (f"Error at line {idx} ('{line}'):\n"
                         f"{orig}\n"
                         f"{pointer_line}\n"
                         f"{e}")
            errors.append(error_msg)
    if errors:
        raise SyntaxError("\n".join(errors))
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
