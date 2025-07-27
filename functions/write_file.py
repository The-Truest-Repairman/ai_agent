import os
from google.genai import types
def write_file(working_directory, file_path, content):
    absolute_working_dir = os.path.abspath(working_directory)
    full_path = os.path.abspath(os.path.join(absolute_working_dir, file_path))
    
    #First check for proper directory inputs 
    if not full_path.startswith(absolute_working_dir): #if the path is not in the working directory, ERROR
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    try:
        if not os.path.exists(full_path): #Check that the path to the file does not exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True) #Make the file directory in the specified path if doesn't exist
        with open(full_path, "w") as f: #Overwrite the new file with content
            f.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        
    except Exception as e:
        return f"Error: {e}"
    
#Schema declaration to help LLM understand what the functions do and their arguments    
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="This function writes files base on passed content argument, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write, relative to the working directory.",
            ),
              "content": types.Schema(
                type=types.Type.STRING,
                description="The content that will be written to the file specified in file_path, relative to the working directory. Creates the file if it does not exist and overwrites if the file already exists.",
            ),
        },
    ),
)
    
    