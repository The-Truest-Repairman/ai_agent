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

config=types.GenerateContentConfig(
    tools=[available_functions], system_instruction=system_prompt
)


def parse_input(args):
    #First check for args length
    match(len(args)):
        case 1: #No prompt detected
            script_name = args[0]
            print("Error: No argument provided.")
            sys.exit(1) # Exit with an error code
        case 2: #Prompt but no flags
            script_name = args[0]
            user_prompt = args[1]
            flags = []
            return user_prompt, flags
        case x if x > 2: #Prompt + flags
            script_name = args[0]
            user_prompt = args[1]
            flags = args[2:]
            return user_prompt, flags
        case _: #default case, raise error
            raise Exception("Improper input...expecting: <scriptname.py> <'prompt'> <optional flags>")
            
    
#Check for proper inputs and parse arguments
user_prompt, flags = parse_input(sys.argv)



#List of user prompts to keep track for continuous conversation
messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

#Call generate_content with message

response = client.models.generate_content(
    model=model_name,
    contents=messages,
    config = config
)
#Check for function calls and save them into new var
function_call_part = None
if response.function_calls:
    function_call_part = response.function_calls[0]  # Get the first function call

#Print response helper function to better format the response
def print_response_info(response, user_prompt, function_call_part, verbose=False):
    if verbose:
        print(f"User prompt: {user_prompt}\n")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}\n")
    
    if function_call_part is not None:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    
    
    print(f"\n--------------RESPONSE----------------\n\n{response.text}\n")
    print("--------END OF RESPONSE OUTPUT--------")
        

print_response_info(response, user_prompt, function_call_part, "--verbose" in flags)
