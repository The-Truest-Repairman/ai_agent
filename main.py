import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions import *
from prompts import system_prompt
from call_function import available_functions, call_function


def main():
    #Initialize agent with API key and set some useful vars
    load_dotenv()

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    verbose = "--verbose" in sys.argv
    
    def parse_input(args):
        if len(args) < 2:
            print("Error: No argument provided.")
            sys.exit(1)
        
        return args[1], args[2:] if len(args) > 2 else []

    #Check for proper inputs and parse arguments
    user_prompt, flags = parse_input(sys.argv)
  

    #List of user prompts to keep track for continuous conversation
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]
    
    ##################################################
    #Call generate_content looped but
    
    ###################################################

   ##Handle responses function:
   # def handle_response(response):
   #     #Check for function calls and save them into new var
   #    function_call_part = None
   #    if response.function_calls:
   #         function_call_part = response.function_calls[0]  # Get the first function call
   #    for candidate in response.candidates:
   #         #Build list of candidate responses and add it to our messages list
   #         messages.append(candidate.content)

    #handle_response(response)

    generate_content(client, messages, verbose)

def generate_content(client, messages, verbose):
    response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=messages,
    config = types.GenerateContentConfig(
        tools=[available_functions], system_instruction=system_prompt
        )
    )
    #Output to the terminal 
    if verbose:
        print(f"\nPrompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}\n")

    # Handle function calls
    if not response.function_calls:
        return response.text
    
    function_responses = []
    for function_call_part in response.function_calls:
        function_call_result = call_function(function_call_part, verbose)
        #Append result.content to our messages list
        messages.append(function_call_result.parts)

        if not function_call_result or not function_call_result.parts[0].function_response.response:
            raise Exception("Fatal Error: no function response")

        if verbose:
            print(f"-> {function_call_result.parts[0].function_response.response}")
        
        function_responses.append(function_call_result.parts[0])
        print(f"\n--------------RESPONSE----------------\n\n{response.text}\n")
        print("--------END OF RESPONSE OUTPUT--------")
    if not function_responses:
        raise Exception("no function responses generated, exiting")
   

if __name__ == "__main__":
    main()