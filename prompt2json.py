import os, re, json
from dotenv import load_dotenv
import openai
from helpers import get_filter_response, get_summary, get_type

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

# Get the user prompt
user_prompt = input("请输入您的排课需求：")

# Set the API key
openai.api_key = openai_api_key

# Initialize the OpenAI client with your API key
client = openai.OpenAI(api_key=openai_api_key)

filter_status = get_filter_response(client, user_prompt)
if filter_status == None:
    print("Error: check prompt library (filter).")
    exit(0)
print(filter_status)

if filter_status == "False":
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
exit(0)
# Write the list of JSON objects to a file
with open('output_list.json', 'w', encoding='utf-8') as file:
    json.dump(json_list, file, ensure_ascii=False, indent=4)