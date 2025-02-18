# blor 0.6
# blor compiler based by python , Rewis and Wren
# This is a compiler for the blor language, which is a simple language that is a subset of python
# The compiler is written in python, and compiles the bloc code to python code
# The compiler is written in a simple way, to make it easy to understand


import re
import os
import sys
# Insert the directory containing BlorImportModule.py into sys.path.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "source"))
from BlorImportModule import process_import  # Now this should import correctly

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

def translate_line(line, stored, alias_disabled=False):
    # Pass through raw Python lines prefixed by "py:".
    if line.lstrip().startswith("py:"):
        return [line.lstrip()[3:].lstrip()], stored
    # New branch: support alias import for lines like "import Random" (with uppercase first letter)
    alias_match = re.match(r'^import\s+([A-Z][a-zA-Z0-9_]*)$', line.lstrip())
    if alias_match and not alias_disabled:
        alias = alias_match.group(1)
        # Updated: use the alias as the module name.
        constructed = f"from {alias.lower()} import module.{alias}"
        try:
            py_code = process_import(constructed)
            return [py_code], stored
        except Exception as e:
            raise SyntaxError(e)
    
    # New branch: pass through Python lines unchanged.
    if line.lstrip().startswith("import ") or line.lstrip().startswith("return "):
        return [line], stored

    # New branch: allow generic assignment lines (e.g. random = Random(0,1)) to pass through.
    if re.match(r'^[a-zA-Z_]\w*\s*=\s*.+$', line):
        return [line], stored

    # New branch: support “import Alias” syntax only if not disabled.
    if not alias_disabled:
        import_match = re.match(r'^import\s+([a-zA-Z_]\w*)$', line)
        if import_match:
            alias = import_match.group(1)
            # Updated: use the alias as the module name.
            constructed = f"from {alias.lower()} import module.{alias}"
            try:
                py_code = process_import(constructed)
                return [py_code], stored
            except Exception as e:
                raise SyntaxError(e)
    
    # New: Allow simple module function calls like "Zobtest.call()"
    if re.match(r'^\w+\.\w+\(\)$', line):
        return [line], stored

    # New: Check for common typos using regex with word boundaries.
    typo_map = {
        r"\bst\.": "str.",
        # "it.": "int."  # (removed to avoid matching within "list")
        "oup.println": "outp.println",
        "oup.print": "outp.print",
        "publc": "public",
        "privte": "private",
        "functon": "function",
        "funcion": "function"
    }
    for pattern, correction in typo_map.items():
        if re.search(pattern, line):
            suggested = re.sub(pattern, correction, line)
            raise SyntaxError(f"Unsupported syntax '{line}'. Did you mean '{suggested}'?")
    
    lines_out = []
    # New: Module header from .zob files.
    if re.match(r'^public\s+module\s+(\w+)\s*\{', line):
        m = re.match(r'^public\s+module\s+(\w+)\s*\{', line)
        return [f"# Begin module {m.group(1)}"], stored

    # New: Variable assignments with type prefix.
    elif re.match(r'^(int|str)\.([a-zA-Z_]\w*)\s*=\s*(.+)$', line):
        m = re.match(r'^(int|str)\.([a-zA-Z_]\w*)\s*=\s*(.+)$', line)
        return [f"{m.group(2)} = {m.group(3).strip()}"], stored

    # New: Blor import commands.
    if line.startswith("from "):
        try:
            py_code = process_import(line)
            return [py_code], stored
        except Exception as e:
            raise SyntaxError(e)

    # outp.println() handling.
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

    # Generic variable input.
    m = re.match(r'^(int|str)\.([a-zA-Z_]\w*)\.input\((.*?)\)$', line)
    if m:
        if m.group(1) == "int":
            lines_out = [
                "try:",
                f"    {m.group(2)} = int(input({m.group(3).strip()}))",
                "except ValueError:",
                f"    print('Invalid input for {m.group(2)}')",
                f"    {m.group(2)} = 0"
            ]
        else:
            lines_out = [f"{m.group(2)} = input({m.group(3).strip()})"]
        return lines_out, stored

    elif re.match(r'^while\.loop\((.*?)\)$', line):
        m = re.match(r'^while\.loop\((.*?)\)$', line)
        lines_out = [f"while {clean_condition(m.group(1).strip())}:"]
    elif re.match(r'^else if (.*)$', line):
        m = re.match(r'^else if (.*)$', line)
        lines_out = [f"elif {clean_condition(m.group(1).strip())}:"]
    elif re.match(r'^if (.*)$', line):
        m = re.match(r'^if (.*)$', line)
        lines_out = [f"if {clean_condition(m.group(1).strip())}:"]
    elif line == "else":
        lines_out = ["else:"]
    # Private main function syntax.
    elif re.match(r'^private\s+main\s+function[\(\{]', line):
        return ["if __name__ == '__main__':"], stored
    # Updated: support function definitions with parameters (accept optional trailing '{')
    elif re.match(r'^(public new|private main)\s+function\s+(\w+)\s*\((.*)\)\s*(\{)?\s*$', line):
        m = re.match(r'^(public new|private main)\s+function\s+(\w+)\s*\((.*)\)\s*(\{)?\s*$', line)
        func_name = m.group(2)
        params_list = m.group(3).strip()
        if params_list:
            # Split by comma and remove type prefixes (e.g. "str." or "int.").
            params = [p.strip().split('.')[-1] for p in params_list.split(',')]
            params_str = ", ".join(params)
        else:
            params_str = ""
        lines_out = [f"def {func_name}({params_str}):"]
    # Function calls.
    elif re.match(r'^function\.(\w+)\((.*?)\)$', line):
        m = re.match(r'^function\.(\w+)\((.*?)\)$', line)
        let_mod = globals().get("__last_imported_module__")
        lines_out = [f"{let_mod}.{m.group(1)}({m.group(2).strip()})" if let_mod else f"{m.group(1)}({m.group(2).strip()})"]
        return lines_out, stored
    elif line == "break":
        lines_out = ["break"]
    # Module initialization.
    elif re.match(r'^(\w+)\.init$', line):
        m = re.match(r'^(\w+)\.init$', line)
        return [f"# Initialize module {m.group(1)}"], stored
    # Allow module function calls such as "Zobtest.call()".
    elif re.match(r'^(\w+)\.(\w+)\(\)$', line):
        return [line], stored
    else:
        raise SyntaxError(f"Unsupported syntax in line: '{line}'. Please verify your Blor syntax.")
    return lines_out, stored

def blor_to_python(blor_code, alias_disabled=False):
    python_code = []
    errors = []
    indent = 0
    stored_content = ""
    for idx, orig in enumerate(blor_code.splitlines(), start=1):
        raw_line = orig.rstrip('\n')
        if not raw_line.strip():
            continue
        line = raw_line.strip()
        if line.startswith("//"):
            continue
        while line.startswith("}"):
            indent = max(indent - 1, 0)
            line = line[1:].strip()
        increase = False
        # Correct the method call below:
        if line.endswith("{"):
            increase = True
            line = line[:-1].strip()
        line = line.replace("{", "").replace("}", "").strip()
        if not line:
            continue
        try:
            trans_lines, stored_content = translate_line(line, stored_content, alias_disabled)
            for t in trans_lines:
                python_code.append("    " * indent + t)
            if increase:
                indent += 1
        except SyntaxError as e:
            offset = len(orig) - len(orig.lstrip())
            pointer_line = " " * offset + "^"
            errors.append(f"Error at line {idx} ('{line}'):\n{orig}\n{pointer_line}\n{e}")
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
        # Uncomment to debug:
        # print("Generated Python code:\n", python_code)
        exec(python_code, globals())
    except SyntaxError as e:
        print(f"Syntax Error: {e}")

if __name__ == "__main__":
    main()
