import json
import openai
from filter_summary_infotype import file_reader_json, get_filter_response, get_summary, get_type
from generate_json_by_info_type import get_json
import config
config.init()

# Get user input:
user_input = file_reader_json(config.file_input)

# Get the API key from environment variables
openai_api_key = config.openai_api_key

# Get the user prompt
user_prompt = user_input["input_info"]
output_filename = user_input["output_filename"]

# Set the API key
openai.api_key = openai_api_key

# Initialize the OpenAI client with your API key
client = openai.OpenAI(api_key=openai_api_key)

filter_status = get_filter_response(client, user_prompt)
if filter_status == None:
    print("Error: check prompt library (filter).")
    exit(0)
print(filter_status)

if filter_status == False:
    print("您的输入似乎和排课无关，请重新尝试。")
    exit(0)

summary = get_summary(client, user_prompt)
if summary == None:
    print("Error: check prompt library (summary).")
    exit(0)
print(summary)

print(" ")
json_list = []

for prompt in summary:
    print(prompt)
    type = get_type(client, prompt)
    print(type)
    # further process to json
    json_list.append(get_json(client, prompt, type))

print("finished")
    
# Write the list of JSON objects to a file
with open(output_filename, 'w', encoding='utf-8') as file:
    json.dump(json_list, file, ensure_ascii=False, indent=4)

# print(json_list)