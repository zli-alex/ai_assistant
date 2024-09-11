import config as config
from filter_summary_infotype_split import get_openai_response, get_openai_response_binary
import json
from parse_schedule_info import relevance_gradeclass, relevance_teacher, relevance_course, relevance_constraintType
from parse_schedule_info import parse_gradeclass, parse_teacher, parse_course, parse_perioddays, parse_limits, parse_constraint_type
from parse_schedule_info import get_periodday_detailed, parse_Movecourse
from json_schedule_info_getter import get_classes, get_courses, get_teachers, get_teachertimecluster,multi_course
from read_file import file_reader

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

def get_json(client, prompt, type, debug_info = True):
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
    
    # ------ Some Hardcoding based on type : might be up to change ------
    if relevance_constraintType(client, prompt):
        if type == "EVENODDLINK":
            data["constraintJsons"]["type"] = "EVENODDLINK"
            data["constraintJsons"]["constraintType"] = "MAX_ASSIGN" # must assign
        elif type == "COURSESAMETIMELIMIT":
            data["constraintJsons"]["constraintType"] = "MAX_ASSIGN"
            data["constraintJsons"]["type"] = "MAX_SAME_TIME"
        elif type == "TEACHERTIMEMUTEX":
            data["constraintJsons"]["mutexType"] = "ALL"
        elif type == "COURSE2COURSE":
            data["constraintJsons"].update({
                "constraintType":"MUST_ASSIGN",
                "gap":9,
                "frequency":0
            })
        else:
            data["constraintJsons"]["constraintType"] = parse_constraint_type(client, prompt)
            if type == "CONSECUTIVECOURSE":
                data["constraintJsons"].update({
                        "gap":0,
                        "constraintType":"MUST_ASSIGN",
                        "consecutiveType":"FIXED",
                        "perioddayType":"DAY",
                        "limitType":"EXACT"
                    })
            elif type in ["TEACHERDAYLIMIT", "TEACHERPERIODLIMIT", "TEACHERTIME"]:
                data["constraintJsons"]["teacherType"] = "TEACHER"
    
    # ------ parse the min max limits ------
    
    if type in ["CONSECUTIVECOURSE", "COURSEDAYLIMIT", "COURSEPERIODLIMIT", "COURSESAMETIMELIMIT", "COURSETIME", "TEACHERDAYLIMIT", "TEACHERPERIODLIMIT", "TEACHERTIME"]:
        data["constraintJsons"].update(parse_limits(client, prompt, type))
        
    # ------ Special Cases discussion
    
    if type in ["CONSECUTIVECOURSE"]:
        data["constraintJsons"]["periodDayClusters"] = get_periodday_detailed(parse_perioddays(client, prompt))
    else:
        periodday_info = parse_perioddays(client, prompt)
        if debug_info:
            print(periodday_info)
        if len(periodday_info) > 0:
            data["constraintJsons"]["periodDays"] = periodday_info
    
    if type == "TEACHERTIMECLUSTER":
        cluster_info = {"minConsecutive":2, "maxConsecutive":2, "minClusterSize":2, "maxClusterSize":2}
        teacher_constraints = parse_teacher(client, prompt)
        if debug_info:
            print(teacher_constraints)
        data["constraintJsons"]["teacherTimeClusters"] = get_teachertimecluster(teacher_constraints, cluster_info)
        return data
    
    if type == "TEACHERTIMEMUTEX":
        
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
                
            data["constraintJsons"]["error"] = False
        else:
            raise ValueError("One or less teachers are recognized in your database.")

        return data
    
    if type == "MOVECOURSE":
        move_courses_constraints = parse_Movecourse(client, prompt)
        if debug_info:
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

        return data
    
    # ------ general case discussion
    
    if relevance_gradeclass(client, prompt):
        gradeclass_constraints = parse_gradeclass(client, prompt)
        data["constraintJsons"]["classes"] = get_classes(gradeclass_constraints)

    if relevance_teacher(client, prompt):
        teacher_constraints = parse_teacher(client, prompt)
        data["constraintJsons"]["teachers"] = get_teachers(teacher_constraints)

    if relevance_course(client, prompt):
        courses_constraints = parse_course(client, prompt)

        # Handle multi_course cases based on type
        if type == "EVENODDLINK":
            data["constraintJsons"].update(multi_course(courses_constraints))
        if type == "COURSE2COURSE":
            temp = multi_course(courses_constraints)
            temp["prevCourse"] = temp["courseA"]
            temp["nextCourse"] = temp["courseB"]
            temp.pop("courseA", None)
            temp.pop("courseB", None)
            data["constraintJsons"].update(temp)
        elif type == "CONSECUTIVECOURSE":
            temp = multi_course(courses_constraints)
            temp["acourse"] = temp["courseA"]
            temp["bcourse"] = temp["courseB"]
            temp.pop("courseA", None)
            temp.pop("courseB", None)
            data["constraintJsons"].update(temp)
        else:
            data["constraintJsons"]["courses"] = get_courses(courses_constraints)
    
    if type == "EVENODDLINK":
        courseA = data["constraintJsons"]["courseA"]["name"]
        evenodd_instruction = f"再以下用户提示词中课程{courseA}是安排在单周吗？"
        response = get_openai_response_binary(client, evenodd_instruction, prompt)
        if response:
            data["constraintJsons"]["courseAOption"] = "ODD"
        else:
            data["constraintJsons"]["courseAOption"] = "EVEN"
    
    return data