import re
import os

def process_import(line):
    """
    Process a Blor import command.
    Expects a command like:
        from importfile.zob import module.callit
    Instead of generating a Python import statement,
    this function reads and compiles the .zob file,
    strips out module definition headers/footers,
    wraps the result in a Python class, and updates globals.
    """
    m = re.match(r'^from\s+([\w./]+\.zob)\s+import\s+module\.(\w+)$', line)
    if not m:
        raise SyntaxError("Invalid import command syntax.")
    zob_file = m.group(1)  # e.g. "importfile.zob"
    module_name = m.group(2)  # e.g. "callit"
    # Resolve full path to the .zob file
    zob_full_path = os.path.join("/workspaces/blorpy", "scr", "test", "importtest", zob_file)
    if not os.path.exists(zob_full_path):
        raise FileNotFoundError(f"No such file: {zob_full_path}")
    with open(zob_full_path, "r") as f:
        zb_code = f.read()
    # ---- Strip out module header/footer ----
    lines = zb_code.splitlines()
    filtered = []
    for l in lines:
        if re.match(r'^public\s+module\s+\w+\s*\{', l.strip()):
            continue
        if l.strip() == "}":
            continue
        filtered.append(l)
    cleaned_code = "\n".join(filtered)
    # -----------------------------------------
    # Compile the cleaned .zob code using the Blor compiler.
    from blorc_compiler import blor_to_python
    compiled_module = blor_to_python(cleaned_code)
    # Wrap the compiled module code inside a class definition.
    wrapped = f"class {module_name}:\n"
    for line in compiled_module.splitlines():
        wrapped += "    " + line + "\n"
    # Add a static init() method that does nothing.
    wrapped += f"    @staticmethod\n"
    wrapped += f"    def init():\n"
    wrapped += f"        pass\n"
    # Append code to update global namespace with module attributes.
    update_globals = (
        f"globals().update({{k: getattr({module_name}, k) for k in dir({module_name}) if not k.startswith('__')}})"
    )
    # Return the wrapped code, module initialization call (which now does nothing), and globals update.
    return f"{wrapped}\n{module_name}.init()\n{update_globals}"

