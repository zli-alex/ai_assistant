import json
import argparse
import openai
from filter_summary_infotype_split import  get_filter_response
from filter_summary_infotype_split import get_summary, get_type, get_split_prompt
from generate_json_by_info_type import get_json
from read_file import file_reader_json
import config
config.init()

def run_schedule_chatbot(user_input_file, output_filename, summary_split_on = False, debug_info = False):
    # Get user input:
    user_input = file_reader_json(user_input_file)

    # Get the API key from environment variables
    openai_api_key = config.openai_api_key

    # Get the user prompt
    user_prompt = user_input["input_info"]

    # Set the API key
    openai.api_key = openai_api_key

    # Initialize the OpenAI client with your API key
    client = openai.OpenAI(api_key=openai_api_key)

    filter_status = get_filter_response(client, user_prompt)
    if filter_status == None:
        print("Error: check prompt library (filter).")
        exit(0)
    if debug_info:
        print(f"Relevance filter: {filter_status}")

    if filter_status == False:
        print("您的输入似乎和排课无关，请重新尝试。")
        exit(0)

    summary = get_summary(client, user_prompt, summary_split_on)
    if summary == None:
        print("Error: check prompt library (summary).")
        exit(0)
    if debug_info:
        print(f"Summary Output {summary}")
    
    json_list = []

    for prompt in summary:
        if debug_info:
            print(" ")
            print(prompt)
        type = get_type(client, prompt)
        if debug_info:
            print(f"Type: {type}")
        subprompts = get_split_prompt(client, prompt, type)
        if debug_info:
            print(f"Split prompts {subprompts}")
        for subprompt in subprompts:
            # further process to json
            json_list.append(get_json(client, subprompt, type, debug_info = debug_info))
    if debug_info:
        print("finished\n\n")
        
    # Write the list of JSON objects to a file
    with open(output_filename, 'w', encoding='utf-8') as file:
        json.dump(json_list, file, ensure_ascii=False, indent=4)

    # print(json_list)

if __name__ == "__main__":
    summary_split_on = False
    
    # Create the parser
    parser = argparse.ArgumentParser(description="Process some arguments.")

    # Add an optional argument
    parser.add_argument(
        '--config', 
        type=str, 
        default=None, 
        help='Optional configuration string, e.g., "summary"'
    )

    # Parse the arguments
    args = parser.parse_args()

    # Check if "summary" is in the provided configuration
    if args.config and "summarysplit" in args.config:
        summary_split_on = True
        print("Summary with Split function is switched on.")

    run_schedule_chatbot(user_input_file= config.file_input, output_filename= config.file_output, summary_split_on=summary_split_on, debug_info= True)