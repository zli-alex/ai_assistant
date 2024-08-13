from helpers import file_reader, get_openai_response
import json
from helper_parse import relevance_gradeclass, relevance_teacher, relevance_course
from helper_parse import parse_gradeclass, parse_teacher, parse_course
from helper_info_getter import get_classes, get_courses, get_teachers

def str2json(answer):
    """Convert from string (markdown format) to json (dictionaries)
        limitations: very naive, cannot handle subsetted information

    Args:
        answer (str): markdown str format of json

    Returns:
        dict: json information in dictionary
    """
    answer.replace('\\"', '"')
    start = answer.find("{")
    end = answer.rfind("}")
    data = json.loads(answer[start:end+1])
    return data

def get_json(client, prompt, type):
    """Product the json (dictonary) data for a given prompt

    Args:
        client (openai.OpenAI): OpenAI client
        prompt (str): user prompt for course scheduling
        type (str): user prompt scheduling type

    Returns:
        dict: desired json data
    """
    project_id = 458
    
    data = {
        "projectId": project_id,
        "projectScenarioId": 985,
        "type": type,
        "constraintJsons": {}
    }
    
    if type == "CONSECUTIVECOURSE":
        ## process
        return data
    
    if relevance_gradeclass(client, prompt):
        gradeclass_constraints = parse_gradeclass(client, prompt)
        data["constraintJsons"]["classes"] = get_classes(gradeclass_constraints)
    
    if relevance_teacher(client, prompt):
        teacher_constraints = parse_teacher(client, prompt)
        data["constraintJsons"]["teachers"] = get_teachers(teacher_constraints)
    
    if relevance_course(client, prompt):
        courses_constraints = parse_course(client, prompt)
        print(courses_constraints)
        data["constraintJsons"]["courses"] = get_courses(courses_constraints)
        
    
    type_instruction = file_reader("./prompt_library/"+type+"2json.txt")
    response = get_openai_response(client, type_instruction, prompt)
    temp = str2json(response)
    data["constraintJsons"].update(temp)
    return data