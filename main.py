import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types


#Initialize agent with API key
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

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
            print(f"Prompt received: {user_prompt}")
            return user_prompt, flags
        case x if x > 2: #Prompt + flags
            script_name = args[0]
            user_prompt = args[1]
            flags = args[2:]
            print(f"Prompt received: {user_prompt}\n------------------------------------------------------------------------------------\n")
            return user_prompt, flags
        case _: #default case, raise error
            raise Exception("Improper input...expecting: <scriptname.py> <'prompt'> <optional flags>")
            
    
#Check for proper inputs and parse arguments
user_prompt, flags = parse_input(sys.argv)



#List of user prompts to keep track for continuous conversation
messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

response = client.models.generate_content(model="gemini-2.0-flash-001",contents = messages)
print(response.text)
print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
print(f"Response tokens: {response.usage_metadata.candidates_token_count}")