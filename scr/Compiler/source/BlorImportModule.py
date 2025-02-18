import re
import os
import textwrap
#from blorc_compiler import blor_to_python

def process_import(line):
    m = re.match(r"^from\s+['\"]?([\w\-/\.]+\.zob)['\"]?\s+import\s+module\.(\w+)$", line)
    if m is None:
        from blorc_compiler import blor_to_python  # Import ngay trong hàm để tránh lỗi circular import
        m = re.match(r"^from\s+([a-zA-Z_]\w*)\s+import\s+module\.(\w+)$", line)
        if m is None:
            raise SyntaxError("Invalid import command syntax.")
        alias, module_name = m.groups()
        zob_full_path = os.path.join("/workspaces/blorpy", "zob", "zolib", f"{alias}lib.zob")
    else:
        zob_file, module_name = m.groups()
        zob_full_path = zob_file if os.path.isabs(zob_file) else os.path.join("/workspaces/blorpy", "scr", "test", "importtest", zob_file)
    
    if not os.path.exists(zob_full_path):
        raise FileNotFoundError(f"No such file: {zob_full_path}")
    
    with open(zob_full_path, "r") as f:
        zb_code = f.read()
    
    lines = zb_code.splitlines()
    cleaned_code = "\n".join(l for l in lines if not re.match(r'^public\s+module\s+\w+\s*{', l.strip()) and l.strip() != "}")
    cleaned_code = textwrap.dedent(cleaned_code)
    
    compiled_module = blor_to_python(cleaned_code, alias_disabled=True)
    wrapped = f"class {module_name}:\n" + "\n".join(f"    {line}" for line in compiled_module.splitlines())
    
    if "def blor___call__(" in compiled_module:
        wrapped += "\n    def __new__(cls, *args, **kwargs):\n        return cls.blor___call__(*args, **kwargs)"
    
    wrapped += "\n    @staticmethod\n    def init():\n        pass\n"
    
    make_static = f"""
for k in [k for k in dir({module_name}) if not k.startswith('__')]:
    attr = getattr({module_name}, k)
    if callable(attr):
        setattr({module_name}, k, staticmethod(attr))
"""
    
    update_globals = f"globals().update({{k: getattr({module_name}, k) for k in dir({module_name}) if not k.startswith('__')}})"
    
    globals()["__last_imported_module__"] = module_name
    
    return f"{wrapped}\n{module_name}.init()\n{make_static}\n{update_globals}"
