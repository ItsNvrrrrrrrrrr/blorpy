import re
import os
import textwrap

def process_import(line):
    """
    Process a Blor import command.
    Expects a command like:
        from '/workspaces/blorpy/zob/zob.zob' import module.Zobtest
    Instead of generating a Python import statement,
    this function reads and compiles the .zob file,
    strips out module definition headers/footers,
    removes common leading indentation,
    wraps the result in a Python class, converts its methods to static,
    updates globals, and records the module name.
    """
    m = re.match(r"^from\s+['\"]?([\w\-/\.]+\.zob)['\"]?\s+import\s+module\.(\w+)$", line)
    if not m:
        raise SyntaxError("Invalid import command syntax.")
    zob_file = m.group(1)
    module_name = m.group(2)
    if os.path.isabs(zob_file):
        zob_full_path = zob_file
    else:
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
    cleaned_code = textwrap.dedent(cleaned_code)
    # -----------------------------------------
    from blorc_compiler import blor_to_python
    compiled_module = blor_to_python(cleaned_code)
    wrapped = f"class {module_name}:\n"
    for line in compiled_module.splitlines():
        wrapped += "    " + line + "\n"
    wrapped += "    @staticmethod\n"
    wrapped += f"    def init():\n"
    wrapped += "        pass\n"
    make_static = f"""
for k in [k for k in dir({module_name}) if not k.startswith('__')]:
    attr = getattr({module_name}, k)
    if callable(attr):
        setattr({module_name}, k, staticmethod(attr))
"""
    update_globals = (f"globals().update({{k: getattr({module_name}, k) for k in dir({module_name}) if not k.startswith('__')}})")
    globals()["__last_imported_module__"] = module_name
    return f"{wrapped}\n{module_name}.init()\n{make_static}\n{update_globals}"

