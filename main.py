import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions import *

#Initialize agent with API key and set some useful vars
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
model_name = "gemini-2.0-flash-001"
system_prompt = """
You are a helpful AI coding agent with a personality derived from the character Dean Pelton from the popular TV show "Community". 

You always end your responses with an extremely sexually innappropriate, often over-the-top, and sometimes insecure quip in the style of Dean Pelton. 

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

#Create a list of available functions for the LLM to use
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)
#Make a dictionary of functions available to call
functions = {"get_files_info": get_files_info,
             "get_file_content": get_file_content,
             "run_python_file": run_python_file,
             "write_file": write_file
             }

config=types.GenerateContentConfig(
    tools=[available_functions], system_instruction=system_prompt
)
def parse_input(args):
    if len(args) < 2:
        print("Error: No argument provided.")
        sys.exit(1)
    
    return args[1], args[2:] if len(args) > 2 else []

#Check for proper inputs and parse arguments
user_prompt, flags = parse_input(sys.argv)
verbose = "--verbose" in flags

#List of user prompts to keep track for continuous conversation
messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

##################################################
#Call generate_content with message
response = client.models.generate_content(
    model=model_name,
    contents=messages,
    config = config,
    
)
###################################################

#Check for function calls and save them into new var
function_call_part = None
if response.function_calls:
    function_call_part = response.function_calls[0]  # Get the first function call

def call_function(function_call_part, verbose=False):
    if not function_call_part:
        return None
        
    function_name = function_call_part.name
    function_args = dict(function_call_part.args)  # Create a copy
    function_args["working_directory"] = "./calculator"

    # Print before calling
    if verbose:
        print(f"Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")

    # Check if function exists and call it
    if function_name not in functions:
        response_data = {"error": f"Unknown function: {function_name}"}
    else:
        function_result = functions[function_name](**function_args)
        response_data = {"result": function_result}

    return types.Content(
        role="tool",
        parts=[types.Part.from_function_response(name=function_name, response=response_data)]
    ) 



#Output to the terminal 
if verbose:
    print(f"User prompt: {user_prompt}\n")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}\n")

# Handle function calls
function_call_part = response.function_calls[0] if response.function_calls else None
function_call_result = call_function(function_call_part, verbose)

if not function_call_result or not function_call_result.parts[0].function_response.response:
    raise Exception("Fatal Error: no function response")

if verbose:
    print(f"-> {function_call_result.parts[0].function_response.response}")

print(f"\n--------------RESPONSE----------------\n\n{response.text}\n")
print("--------END OF RESPONSE OUTPUT--------")