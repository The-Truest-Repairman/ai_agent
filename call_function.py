from functions import *
from google.genai import types
from config import WORKING_DIR

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

def call_function(function_call_part, verbose=False):
        if not function_call_part:
            return None
        
        #Make a dictionary of functions available to call
        functions_list = {
             "get_files_info": get_files_info,
             "get_file_content": get_file_content,
             "run_python_file": run_python_file,
             "write_file": write_file
        }

        function_name = function_call_part.name
        function_args = dict(function_call_part.args)  # Create a copy
        function_args["working_directory"] = WORKING_DIR

        # Print before calling
        if verbose:
            print(f"Calling function: {function_name}({function_args})")
        else:
            print(f" - Calling function: {function_name}")

        # Check if function exists and call it
        if function_name not in functions_list:
            response_data = {"error": f"Unknown function: {function_name}"}
        else:
            function_result = functions_list[function_name](**function_args)
            response_data = {"result": function_result}

        return types.Content(
            role="tool",
            parts=[types.Part.from_function_response(name=function_name, response=response_data)]
        ) 