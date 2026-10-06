import re

def insert_import(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "from langfuse.decorators import observe" not in content:
        content = re.sub(r"(import logging\n)", r"\1from langfuse.decorators import observe, langfuse_context\n", content)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def add_decorator(file_path, func_name, decorator_str="@observe()"):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Simple regex to find def <func_name>(...
    pattern = r"^(async def |def )(" + func_name + r"\b\s*\()"
    
    def repl(m):
        # check if it already has the decorator
        return decorator_str + "\n" + m.group(1) + m.group(2)
        
    if decorator_str not in content:
        content = re.sub(pattern, repl, content, flags=re.MULTILINE)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

# main.py
insert_import("api/main.py")
add_decorator("api/main.py", "_run_audit_pipeline", '@observe(name="audit_pipeline")')

# stages
stages = ["claims", "retraction", "stats", "citations", "code_data", "grade", "extract"]
for stage in stages:
    path = f"api/stages/{stage}.py"
    insert_import(path)
    add_decorator(path, "run", f'@observe(name="{stage}_run")')

# llm.py
insert_import("api/llm.py")
add_decorator("api/llm.py", "call_llm", '@observe(as_type="generation", name="call_llm")')
