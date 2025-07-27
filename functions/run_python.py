import os, subprocess
from google.genai import types
def run_python_file(working_directory, file_path, args=[]):
    absolute_working_dir = os.path.abspath(working_directory)
    full_path = os.path.abspath(os.path.join(absolute_working_dir, file_path))
    
    #First check for proper directory inputs 
    if not full_path.startswith(absolute_working_dir): #if the path is not in the working directory, ERROR
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists(full_path): #Check that the path to the file does not exist
        return f'Error: File "{file_path}" not found.'
    if not full_path.endswith(".py"): #Check the the file is a python file
        return f'Error: "{file_path}" is not a Python file.'
    try:
        commands = ["python3", file_path] + args
        result = subprocess.run(commands, timeout=30, capture_output=True, cwd = absolute_working_dir)
        return_string = f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        if result.returncode != 0:
            return_string += f"\nProcess exited with code {result.returncode}"
        #Check that no ooutput is produced 
        if not result.stdout and not result.stderr:
            return_string = "No output produced"
        return return_string
    except Exception as e:
        return f"Error: executing Python file: {e}"


#Schema declaration to help LLM understand what the functions do and their arguments    
schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Function run python commands, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path to the target python file, relative to the working directory. If it's not a python file, return an error",
            ),
            "args": types.Schema(
                type=types.Type.STRING,
                description="Arguments to pass into the python commands.",
            ),
        },
    ),
)

