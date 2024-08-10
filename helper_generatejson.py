import openai
from helpers import file_reader, get_openai_response
from dotenv import load_dotenv
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
        data["constraintJsons"]["classes"] =[]
        response = parse_gradeclass(client, prompt)
        print(response)
        for grade in response.grades:
            if grade.classes == None:
                gradeclass_constraints.append([grade.gradeDcode, None])
            else:
                for curr_class in grade.classes:
                    gradeclass_constraints.append([grade.gradeDcode, curr_class.name])
        print(gradeclass_constraints)
        for gradeDcode, classname in gradeclass_constraints:
            data["constraintJsons"]["classes"].extend(get_class(gradeDcode, classname))
            
    if relevance_teacher(client, prompt) == "True":
        teacher_constraints = []
        data["constraintJsons"]["teachers"] = []
        response = parse_teacher(client, prompt)
        for teacher in response.teachers:
            if teacher.grade == None:
                gradeDcode = None
            else:
                gradeDcode = teacher.grade.gradeDcode
            teacher_constraints.append([teacher.teachername, gradeDcode, teacher.coursename])
        print(teacher_constraints)
        for teachername, gradeDcode, coursename in teacher_constraints:
            data["constraintJsons"]["teachers"].extend(get_teacher(teachername, gradeDcode, coursename))
    
    if relevance_course(client, prompt) == "True":
        courses_constraints = []
        data["constraintJsons"]["courses"] = []
        response = parse_course(client, prompt).courses
        for course in response:
            if course.gradeDcode == None or len(course.gradeDcode) == 0:
                courses_constraints.append([course.coursename, None])
            else:
                courses_constraints.append([course.coursename, course.gradeDcode])
        print(courses_constraints)
        for subject, grade_list in courses_constraints:
            for grade in grade_list:
                data["constraintJsons"]["courses"].extend(get_course(grade, subject))
    
    type_instruction = file_reader("./prompt_library/"+type+"2json.txt")
    response = get_openai_response(client, type_instruction, prompt)
    temp = str2json(response)
    data["constraintJsons"].update(temp)
    return data