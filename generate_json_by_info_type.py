import config
from filter_summary_infotype import file_reader, get_openai_response
import json
from parse_schedule_info import relevance_gradeclass, relevance_teacher, relevance_course, relevance_periodday
from parse_schedule_info import parse_gradeclass, parse_teacher, parse_course, parse_perioddays
from parse_schedule_info import get_periodday_detailed, parse_Movecourse
from json_schedule_info_getter import get_classes, get_courses, get_teachers, get_teachertimecluster,multi_course

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
    
    if relevance_periodday(client, prompt):
        if type in ["CONSECUTIVECOURSE"]:
            data["constraintJsons"]["periodDayClusters"] = get_periodday_detailed(parse_perioddays(client, prompt))
        else:
            data["constraintJsons"]["periodDays"] = parse_perioddays(client, prompt)
    
    if type == "TEACHERTIMECLUSTER":
        type_instruction = file_reader("./prompt_library/"+type+"2json.txt")
        response = get_openai_response(client, type_instruction, prompt)
        cluster_info = str2json(response)
        teacher_constraints = parse_teacher(client, prompt)
        print(teacher_constraints)
        data["constraintJsons"]["teacherTimeClusters"] = get_teachertimecluster(teacher_constraints, cluster_info)
        return data
    
    if type == "TEACHERTIMEMUTEX":
        type_instruction = file_reader("./prompt_library/"+type+"2json.txt")
        response = get_openai_response(client, type_instruction, prompt)
        mutex_info = str2json(response)
        
        teacher_constraints = parse_teacher(client, prompt)
        teacher_courses_info = get_teachertimecluster(teacher_constraints)

        if len(teacher_courses_info) >= 2:
            data["constraintJsons"]["ateacher"] = teacher_courses_info[0]["teacher"]
            data["constraintJsons"]["aTeacherId"] = teacher_courses_info[0]["teacher"]["uid"]
            data["constraintJsons"]["aCourses"] = teacher_courses_info[0]["courses"]
            if len(teacher_courses_info[0]["courses"]) == 1:
                data["constraintJsons"]["acourse"] = teacher_courses_info[0]["courses"][0]["name"]
                data["constraintJsons"]["aCourseId"] = teacher_courses_info[0]["courses"][0]["uid"]
            else:
                data["constraintJsons"]["acourse"] = None
                data["constraintJsons"]["aCourseId"] = None
            data["constraintJsons"]["bteacher"] = teacher_courses_info[1]["teacher"]
            data["constraintJsons"]["bTeacherId"] = teacher_courses_info[1]["teacher"]["uid"]
            data["constraintJsons"]["bCourses"] = teacher_courses_info[1]["courses"]
            if len(teacher_courses_info[1]["courses"]) == 1:
                data["constraintJsons"]["bcourse"] = teacher_courses_info[1]["courses"][0]["name"]
                data["constraintJsons"]["bCourseId"] = teacher_courses_info[1]["courses"][0]["uid"]
            else:
                data["constraintJsons"]["bcourse"] = None
                data["constraintJsons"]["bCourseId"] = None
        else:
            raise ValueError("One or less teachers are recognized in your database.")
        
        data["constraintJsons"].update(mutex_info)

        return data
    
    if type == "MOVECOURSE":
        move_courses_constraints = parse_Movecourse(client, prompt)
        print(move_courses_constraints)
        
        data["constraintJsons"]["moveCourseDetails"] = []

        for gradeDcode, classname, coursename in move_courses_constraints:
            courseInfo = get_courses([[coursename, [gradeDcode]]])
            if len(courseInfo) == 0:
                raise ValueError(f"Course you have entered with {coursename} in {gradeDcode} is not in your database.")
            classInfo = get_classes([[gradeDcode, classname]])
            if len(classInfo) == 0:
                raise ValueError(f"Class you have entered with {gradeDcode} named {classname} is not in your database.")
            data["constraintJsons"]["moveCourseDetails"].append({
                "classes" : {
                    "name" : classInfo[0]["name"],
                    "uid" : classInfo[0]["uid"]
                },
                "courses" : {
                    "name" : courseInfo[0]["name"],
                    "uid" : courseInfo[0]["uid"]
                }
            })

        
        print(data)

        return data
    
    if relevance_gradeclass(client, prompt):
        gradeclass_constraints = parse_gradeclass(client, prompt)
        data["constraintJsons"]["classes"] = get_classes(gradeclass_constraints)

    if relevance_teacher(client, prompt):
        teacher_constraints = parse_teacher(client, prompt)
        data["constraintJsons"]["teachers"] = get_teachers(teacher_constraints)

    if relevance_course(client, prompt):
        courses_constraints = parse_course(client, prompt)

        # Handle multi_course cases based on type
        if type in ["EVENODDLINK", "CONSECUTIVECOURSE", "COURSE2COURSE"]:
            data["constraintJsons"].update(multi_course(courses_constraints))
        else:
            data["constraintJsons"]["courses"] = get_courses(courses_constraints)

    type_instruction = file_reader("./prompt_library/" + type + "2json.txt")
    if type == "EVENODDLINK":
        type_instruction += str(data["constraintJsons"]["courseA"]["name"])
    response = get_openai_response(client, type_instruction, prompt)
    temp = str2json(response)
    data["constraintJsons"].update(temp)
    return data