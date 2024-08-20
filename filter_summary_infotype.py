import config
import json
from pydantic import BaseModel
def get_openai_response(client, instruction, prompt):
    """Get OpenAI response

    Args:
        client (openai.OpenAI): OpenAI client
        instruction (str): instruction string
        prompt (str): user prompt

    Returns:
        str: response
    """
    response = client.chat.completions.create(
        model=config.model_name,
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": prompt},
        ],
        temperature=config.model_temp
    )
    return response.choices[0].message.content
    
def get_openai_response_structured(client, instruction, prompt, structure):
    """Get OpenAI structured response

    Args:
        client (openai.OpenAI): OpenAI client
        instruction (str): instruction string
        prompt (str): user prompt
        structure (class): a class

    Returns:
        openai.response: Parsed response from openai according to structure defined above
    """
    response = client.beta.chat.completions.parse(
        model=config.model_name,
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": prompt},
        ],
        response_format=structure,
        temperature=config.model_temp
    )
    return response.choices[0].message.parsed

class BinaryResponse(BaseModel):
    response: bool

def get_openai_response_binary(client, instruction, prompt):
    """Get OpenAI structured response

    Args:
        client (openai.OpenAI): OpenAI client
        instruction (str): instruction string
        prompt (str): user prompt

    Returns:
        bool: True or False
    """
    return get_openai_response_structured(client, instruction, prompt, BinaryResponse).response

def file_reader(file_name):
    """Read file as a whole string

    Args:
        file_name (str): path to file (txt)

    Returns:
        str: a very long string of file content
    """
    with open(file_name, encoding='utf-8') as data_file:   
        content = data_file.read()
    return content

def file_reader_json(file_name):
    """Read file as a json

    Args:
        file_name (str): path to file (txt)

    Returns:
        dict: json data
    """
    with open(file_name, encoding='utf-8') as data_file:    
        data = json.load(data_file)
    return data

def get_filter_response(client, prompt):
    """Filter whether the information have anything to do with course scheduling

    Args:
        client (openai.OpenAI): OpenAI client
        prompt (str): user prompt

    Returns:
        bool: True or False
    """
    filter_instruction = file_reader("./prompt_library/preprocess_filter.txt")
    if filter_instruction == None:
        return None
    message = get_openai_response_binary(client, filter_instruction, prompt)
    return message

def get_summary(client, prompt):
    """Get a summary of user prompt

    Args:
        client (openai.OpenAI): OpenAI client
        prompt (str): user prompt

    Returns:
        list[str]: a list of summarized information, each contains only one piece of 
        course scheduling information
    """
    summary_instruction = file_reader("./prompt_library/preprocess_summary.txt")
    if summary_instruction == None:
        return None
    message = get_openai_response(client, summary_instruction, prompt)
    summary = message.strip().split("。")    
    summary = [x for x in summary if x != ""]
    return summary

def get_type(client, prompt):
    """Get the course scheduling type of the user prompt

    Args:
        client (openai.OpenAI): OpenAI client
        prompt (str): user prompt

    Returns:
        str: prompt type (e.g. "TEACHERTIMEMUTEX")
    """
    type_instruction = file_reader("./prompt_library/preprocess_classify.txt")
    if type_instruction == None:
        return None
    message = get_openai_response(client, type_instruction, prompt)
    return message