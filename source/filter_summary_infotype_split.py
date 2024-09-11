import config
import json
from pydantic import BaseModel
from json_schedule_info_getter import get_unique_courses, get_grade2gradeDcode, get_unique_teachers
from read_file import file_reader,file_reader_json

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

def get_filter_response(client, prompt):
    """Filter whether the information have anything to do with course scheduling

    Args:
        client (openai.OpenAI): OpenAI client
        prompt (str): user prompt

    Returns:
        bool: True or False
    """
    filter_instruction = file_reader("../prompt_library/preprocess_filter.txt")
    if filter_instruction == None:
        return None
    message = get_openai_response_binary(client, filter_instruction, prompt)
    return message

def get_summary(client, prompt, summary_split_on):
    """Get a summary of user prompt

    Args:
        client (openai.OpenAI): OpenAI client
        prompt (str): user prompt

    Returns:
        list[str]: a list of summarized information, each contains only one piece of 
        course scheduling information
    """
    if summary_split_on:
        summary_instruction = file_reader("../prompt_library/preprocess_summary_split.txt") 
        message = get_openai_response(client, summary_instruction, prompt)
        subprompts = message.strip().split("。")    
        subprompts = [x for x in subprompts if x != ""]
        return subprompts
    else:   
        summary_instruction = file_reader("../prompt_library/preprocess_summary.txt")
        message = get_openai_response(client, summary_instruction, prompt)
        return [message]
    

def get_type(client, prompt):
    """Get the course scheduling type of the user prompt

    Args:
        client (openai.OpenAI): OpenAI client
        prompt (str): user prompt

    Returns:
        str: prompt type (e.g. "TEACHERTIMEMUTEX")
    """
    type_instruction = file_reader("../prompt_library/preprocess_classify.txt")
    type_instruction += "请注意课程名称、年级名称和教师名称。\n以下是所有课程名称："
    type_instruction += str(get_unique_courses())
    type_instruction += "以下是所有年级名称"
    type_instruction += str(get_grade2gradeDcode().keys())
    type_instruction += "以下是所有教师名称"
    type_instruction += str(get_unique_teachers())

    if type_instruction == None:
        return None
    message = get_openai_response(client, type_instruction, prompt)
    return message

def split_prompt_helper(client, instruction, prompt_list):
    """Split a prompt with LLM

    Args:
        client (openai.OpenAI): OpenAI Client
        instruction (str): split prompt instruction
        prompt_list (list[str]): a list of prompts to be split

    Returns:
        list[str]: a list of subprompts
    """
    subprompts = []
    for prompt in prompt_list:
        message = get_openai_response(client, instruction, prompt)
        temp = message.strip().split("。")    
        temp = [x for x in temp if x != ""]
        subprompts.extend(temp)
    return subprompts

def get_split_prompt(client, prompt, type):
    """Split the prompt given the type

    Args:
        client (openai.OpenAI): OpenAI Client
        prompt (str): user prompt
        type (str): course schedule type of the the user prompt

    Returns:
        list[str]: a list of subprompts
    """
    split_instruction_by_subject = file_reader("../prompt_library/split_prompt_by_course.txt")
    split_instruction_by_subject += "请注意课程名称和年级名称的正确分割。\n以下是所有课程名称："
    split_instruction_by_subject += str(get_unique_courses())
    split_instruction_by_grade = file_reader("../prompt_library/split_prompt_by_grade.txt")
    split_instruction_by_grade += "以下是所有年级名称"
    split_instruction_by_grade += str(get_grade2gradeDcode().keys())
    if type in ["TEACHERDAYLIMIT", "TEACHERPERIODLIMIT", "TEACHERTIME", "TEACHERTIMECLUSTER", "TEACHERTIMEMUTEX"]:
        return [prompt]
    if type in ["COURSESAMETIMELIMIT"]:
        # 初一初二初三的美术和音乐 同一节最多2个班
        # 初一初二初三的美术同一节最多2个班, 初一初二初三的音乐同一节最多2个班
        return split_prompt_helper(client, split_instruction_by_subject, [prompt])
    if type in ["COURSETIME", "COURSEDAYLIMIT", "EVENODDLINK", "CONSECUTIVECOURSE", "COURSE2COURSE"]:
        # 初一初二的劳动课 周五必排1节
        # 初一的劳动课 周五必排1节, 初二的劳动课 周五必排1节
        return split_prompt_helper(client, split_instruction_by_grade, [prompt])
    
    subprompts = split_prompt_helper(client, split_instruction_by_subject, [prompt])
    subprompts = split_prompt_helper(client, split_instruction_by_grade, subprompts)

    return subprompts