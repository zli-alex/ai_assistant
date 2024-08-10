from pydantic import BaseModel
import openai
from typing import Optional
from helpers import file_reader, get_openai_response
from dotenv import load_dotenv
import pandas as pd
import os,json
from helper_parse import relevance_gradeclass, relevance_teacher, relevance_course
from helper_parse import parse_gradeclass, parse_teacher, parse_course
from information_getter import get_class, get_course, get_teacher

def str2json(answer):
    answer.replace('\\"', '"')
    start = answer.find("{")
    end = answer.rfind("}")
    data = json.loads(answer[start:end+1])
    return data

def get_json(client, prompt, type):
    project_id = 458
    
    data = {
        "projectId": project_id,
        "projectScenarioId": 985,
        "type": type,
        "constraintJsons": {}
    }
    
    if relevance_gradeclass(client, prompt) == "True":
        gradeclass_constraints = []
        response = parse_gradeclass(client, prompt)
        print(response)
        for grade in response.grades:
            if grade.classes == None:
                gradeclass_constraints.append([grade.gradeDcode, None])
            else:
                for curr_class in grade.classes:
                    gradeclass_constraints.append([grade.gradeDcode, curr_class.name])
        print(gradeclass_constraints)
        data["constraintJsons"]["classes"] = get_class()
        if len(data["constraintJsons"]["classes"]) == 0:
            data["constraintJsons"]["classes"] = get_classes("./inputs/课程和班级信息.json", gradeclass_constraints)
            
    if relevance_teacher(client, prompt) == "True":
        teacher_constraints = []
        response = parse_teacher(client, prompt)
        for teacher in response.teachers:
            teacher_constraints.append([teacher.teachername, teacher.grade.gradeDcode, teacher.coursename])
        print(teacher_constraints)
        data["constraintJsons"]["teachers"] = get_teachers("./inputs/教师任课信息.json", teacher_constraints)
        if len(data["constraintJsons"]["teachers"]) == 0:
            data["constraintJsons"]["teachers"] = get_teachers("./inputs/教师任课信息.json", teacher_constraints)
    
    if relevance_course(client, prompt) == "True":
        courses_constraints = []
        response = parse_course(client, prompt).courses
        for course in response:
            if course.gradeDcode == None or len(course.gradeDcode) == 0:
                courses_constraints.append([course.coursename, None])
            else:
                courses_constraints.append([course.coursename, course.gradeDcode])
        data["constraintJsons"]["courses"] = get_courses("./inputs/课程和班级信息.json", courses_constraints)
        if len(data["constraintJsons"]["courses"]) == 0:
            data["constraintJsons"]["courses"] = get_courses("./inputs/课程和班级信息.json", courses_constraints)
    
    type_instruction = file_reader("./prompt_library/"+type+"2json.txt")
    response = get_openai_response(client, type_instruction, prompt)
    temp = str2json(response)
    data["constraintJsons"].update(temp)
    return data