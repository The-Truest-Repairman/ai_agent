import os
from google.genai import types
from config import FILE_CHAR_LIMIT
def get_file_content(working_directory, file_path):
    absolute_working_dir = os.path.abspath(working_directory)
    full_path = os.path.abspath(os.path.join(absolute_working_dir, file_path))

    #First check for proper directory inputs 
    if not full_path.startswith(absolute_working_dir):
        return f'Error: Cannot list "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(full_path): #Check that the path is a file
        return f'Error: File not found or is not a regular file: "{file_path}"'
    
    #Try to read the file and catch any exceptions
    try:
        with open(full_path, "r") as f:
            file_content_string = f.read(FILE_CHAR_LIMIT)
            return file_content_string
    except Exception as e:
        return(f"Error: {e}")


#Schema declaration to help LLM understand what the functions do and their arguments    
schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Function to get the contents of a specified file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path to the target file, relative to the working directory.",
            ),
        },
    ),
)
   

    
        
    

