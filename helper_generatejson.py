import openai
from helpers import file_reader, get_openai_response
from dotenv import load_dotenv
import os,json
from helper_parse import relevance_gradeclass, relevance_teacher, relevance_course
from helper_parse import parse_gradeclass, parse_teacher, parse_course
from information_getter import get_class, get_course, get_teacher, get_teachercourse

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
    
    gradeDcodes = []
    if relevance_gradeclass(client, prompt) == "True":
        gradeclass_constraints = []
        data["constraintJsons"]["classes"] =[]
        response = parse_gradeclass(client, prompt)
        print(response)
        for grade in response.grades:
            gradeDcodes.append(grade.gradeDcode)
            if grade.classes == None:
                gradeclass_constraints.append([grade.gradeDcode, None])
            else:
                for curr_class in grade.classes:
                    gradeclass_constraints.append([grade.gradeDcode, curr_class.name])
        print(gradeclass_constraints)
        for gradeDcode, classname in gradeclass_constraints:
            data["constraintJsons"]["classes"].extend(get_class(gradeDcode, classname))
    
    teachernames = []
    if relevance_teacher(client, prompt) == "True":
        teacher_constraints = []
        data["constraintJsons"]["teachers"] = []
        response = parse_teacher(client, prompt)
        for teacher in response.teachers:
            teachernames.append(teacher.teachername)
            if teacher.grade == None:
                gradeDcode = None
            else:
                gradeDcode = teacher.grade.gradeDcode
            teacher_constraints.append([teacher.teachername, gradeDcode, teacher.coursename])
        print(teacher_constraints)
        for teachername, gradeDcode, coursename in teacher_constraints:
            data["constraintJsons"]["teachers"].extend(get_teacher(teachername, gradeDcode, coursename))
    
    coursenames = []
    if relevance_course(client, prompt) == "True":
        courses_constraints = []
        data["constraintJsons"]["courses"] = []
        response = parse_course(client, prompt).courses
        for course in response:
            coursenames.append(course.coursename)
            if course.gradeDcode == None or len(course.gradeDcode) == 0:
                courses_constraints.append([course.coursename, None])
            else:
                courses_constraints.append([course.coursename, course.gradeDcode])
        print(courses_constraints)
        for subject, grade_list in courses_constraints:
            if grade_list == None:
                data["constraintJsons"]["courses"].extend(get_course(None, subject))
            else:
                for grade in grade_list:
                    data["constraintJsons"]["courses"].extend(get_course(grade, subject))
    
    if type == "TEACHERTIMECLUSTER":
        data["constraintJsons"]["teacherTimeClusters"] = []
        data["constraintJsons"].pop("courses", None)
        data["constraintJsons"].pop("teachers", None)
        data["constraintJsons"].pop("classes", None)
        for course in coursenames:
            for teacher in teachernames:
                for grade in gradeDcodes:
                    curr = get_teachercourse(teacher, grade, subject)
                    if len(curr) > 0:
                        data["constraintJsons"]["teacherTimeClusters"].extend(curr)
        return data
    
    if type == "TEACHERTIMEMUTEX":
        print(teachernames)
        try:
            ateachername = teachernames[0]
            bteachername = teachernames[1]
            ateachercourses = get_teachercourse(ateachername, None, None)
            print(ateachercourses)
            ateacher = ateachercourses[0]["teacher"]
            acourses = ateachercourses[0]["courses"]
            bteachercourses = get_teachercourse(bteachername, None, None)
            bteacher = bteachercourses[0]["teacher"]
            bcourses = bteachercourses[0]["courses"]
        except:
            return None
        
        constraint_jsons = {
            "mutexType":"ALL",
            "ateacher": ateacher,
            "aTeacherId" : ateacher["uid"],
            "acourse" : None,
            "aCourses" : acourses,
            "bteacher": bteacher,
            "bTeacherId" : bteacher["uid"],
            "bcourse" : None,
            "bCourses": bcourses
        }
        
        try:
            courseid = data["constraintJsons"]["courses"][0]["courseDcode"]
            constraint_jsons["acourse"] = courseid
            constraint_jsons["bcourse"] = courseid
        except:
            pass
        data["constraintJsons"].update(constraint_jsons)
        data["constraintJsons"].pop("courses", None)
        data["constraintJsons"].pop("teachers", None)
        data["constraintJsons"].pop("classes", None)
        
        return data
    
    type_instruction = file_reader("./prompt_library/"+type+"2json.txt")
    response = get_openai_response(client, type_instruction, prompt)
    temp = str2json(response)
    data["constraintJsons"].update(temp)
    return data