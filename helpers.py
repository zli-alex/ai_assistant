import openai, re, json
def get_openai_response(client, instruction, prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message.content

def file_reader(file_name):
    try:
        file = open(file_name)
    except:
        return None
    content = file.read()
    file.close()
    return content

def get_filter_response(client, prompt):
    filter_instruction = file_reader("./prompt_library/preprocess_filter.txt")
    if filter_instruction == None:
        return None
    message = get_openai_response(client, filter_instruction, prompt) # "True" or "False"
    return message

def get_summary(client, prompt):
    summary_instruction = file_reader("./prompt_library/preprocess_summary.txt")
    if summary_instruction == None:
        return None
    message = get_openai_response(client, summary_instruction, prompt)
    summary = message.strip().split("。")    
    summary = [x for x in summary if x != ""]
    return summary

def get_type(client, prompt):
    type_instruction = file_reader("./prompt_library/preprocess_classify.txt")
    if type_instruction == None:
        return None
    message = get_openai_response(client, type_instruction, prompt)
    return message