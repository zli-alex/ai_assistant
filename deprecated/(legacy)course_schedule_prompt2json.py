import os, re, json
from dotenv import load_dotenv
import openai
from helpers import get_asst_answer, get_summary, get_json

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
filter_asstid = os.getenv("FILTER_ASST_ID")
print(filter_asstid)

# Get the user prompt
user_prompt = input("How can I help you today:")

# Set the API key
openai.api_key = openai_api_key

# Initialize the OpenAI client with your API key
client = openai.OpenAI(api_key=openai_api_key)

filter_status = get_asst_answer(client, user_prompt, filter_asstid)
print(filter_status)

if filter_status == "False":
    print("Please try again with a prompt relevant to course scheduling.")
    exit(0)

summary_asstid = os.getenv("SUMMARY_BYGRADE_ASST_ID")
prompt_type_asstid = os.getenv("PROMPT_TYPE_ASST_ID")
summary = get_summary(client, user_prompt, summary_asstid)
print(summary)
print(" ")
json_list = []

for grade in summary.keys():
    for prompt in summary[grade]:
        curr_prompt = grade + " " + prompt
        print(curr_prompt)
        type = get_asst_answer(client, curr_prompt, prompt_type_asstid)
        print(type)
        asst_id_name = type[1:-1] + "_ASST_ID"
        asst_id = os.getenv(asst_id_name)
        curr_json = get_json(client, curr_prompt, asst_id)
        # print(curr_json)
        json_list.append(curr_json)
        print(" ")

# Write the list of JSON objects to a file
with open('output_list.json', 'w', encoding='utf-8') as file:
    json.dump(json_list, file, ensure_ascii=False, indent=4)