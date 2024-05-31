import os
import ast
import sys

#get current directory
nb_dir = os.getcwd()
code_directory = r'code'
# List your .py files
python_files = ["qaoa.py", "wsqaoarand.py", "wsqaoarow.py"]

# Function to get imports from a file
def get_imports(file):
    file = os.path.join(nb_dir, code_directory, file)
    with open(file, "r") as f:
        tree = ast.parse(f.read(), filename=file)
    return {node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)}

# Collect all imports
all_imports = set()
for file in python_files:
    all_imports.update(get_imports(file))

# Exclude imports containing 'qat'
filtered_imports = {imp for imp in all_imports if 'qat' not in imp}

# Write to requirements.txt
with open("requirements.txt", "w") as req_file:
    for imp in filtered_imports:
        req_file.write(f"{imp}\n")
