from pydantic import BaseModel
import openai
from typing import Optional
from read_file import file_reader, file_reader_json
from filter_summary_infotype_split import get_openai_response_binary, get_openai_response_structured
from json_schedule_info_getter import get_unique_courses, get_unique_teachers, get_unique_classnames, get_grade2gradeDcode
import os
import pandas as pd
import config
# For structured output, need python 3.12

def relevance_gradeclass(client, prompt):
    """Get whether the prompt is relevant to grade and class

    Args:
        client (openai.OpenAI): OpenAI client
        prompt (str): user course scheduling prompt

    Returns:
        bool: True or False
    """
    instruction = "请判断以下用户提示词是否有提及年级或者班级信息。\
                如果有“初一”、“初二”、“初三”等请回答True，如果有班级编号名称等请回答True，如果都没有提及请回答False。\
                用户提示词：初二3班李梅数学课在早上第四节。 请回答：True。用户提示词：张华的物理课只能上每天第九节。\
                请回答：False。"
    response = get_openai_response_binary(client, instruction, prompt)
    return response

def relevance_teacher(client, prompt):
    """Get whether the prompt is relevant to teachers

    Args:
        client (openai.OpenAI): OpenAI client
        prompt (str): user course scheduling prompt

    Returns:
        bool: True or False
    """
    if "老师" in prompt or "教师" in prompt:
        return True
    instruction = "请判断以下用户提示词是否人名,有提及请回答True，并返回。\
                否则请判断用户提示词是否包含“教师”、“老师”、“教职人员”等教职职称，有请回答True。如果都没有提及请回答False。\
                用户提示词：李梅数学课在早上第一节。 请回答：True。用户提示词：美术排在早上第四节。 请回答：False。"
    instruction += "以下是所有教师人名："
    instruction += str(get_unique_teachers())
    response = get_openai_response_binary(client, instruction, prompt)
    return response

def relevance_course(client, prompt):
    """Get whether the prompt is relevant to courses

    Args:
        client (openai.OpenAI): OpenAI client
        prompt (str): user course scheduling prompt

    Returns:
        bool: True or False
    """
    instruction = "请判断以下用户提示词中是否有包括但是不仅限于语文、\
                体活、劳动、班会、班队、心理等的初中学科名称或者初中课程名称。有请回答True，没有请回答False。\
                用户提示词：美术排在早上第四节。 请回答：True。用户提示词：初三周四第九节不排。 请回答：False。"
    instruction += str("包含以下列表中任何一项都请回答True：")
    instruction += str(get_unique_courses())
    response = get_openai_response_binary(client, instruction, prompt)
    return response

def relevance_periodday(client, prompt):
    instruction = "请判断一下用户提示词中是否包含课程时段或者星期信息。\
                    课程时段的格式常为“第几节课”，星期信息的格式常为“星期几”，“周几”或“礼拜几”。\
                    若包含课程时段信息（如第三节课），请回答True；如果包含星期信息（如星期日）， 请回答True；\
                    如果包含“上午”或者“下午”等时间信息，请回答True。如果都没有，请回答False。\
                    特例：“单周”、“双周”。Hint：单周双周说的是单数或双数的整个周，不是一周中的星期几。请回答：False。"
    response = get_openai_response_binary(client, instruction, prompt)
    return response

def relevance_constraintType(client, prompt):
    instruction = "在以下描述的排课场景中，请判断是否需要包含 constraintType 字段。\
                    如果场景中提到的安排是关于必须安排、必须避免、最小或最大安排、单双周安排、或同一时间的最大班级限制，请包含 constraintType 字段。\
                    如果描述的内容没有明确涉及这些条件或是通用信息，不需要包含 constraintType 字段。\
                    例：初一 综合实践1与综合实践2不排同一天。请回答True。\
                    例：初二 美术(单)与音乐(双) 单双周，并且已知courseA是美术。请回答True。\
                    例：钟敏 张慧 不排同一节。请回答False。\
                    例：初二数学老师 不同班级的数学课连着上。请回答False。"
    response = get_openai_response_binary(client, instruction, prompt)
    return response

class Class(BaseModel):
    gradeName: str
    gradeDcode: str
    name: str

class Grade(BaseModel):
    gradeDcode: str
    classes: Optional[list[Class]]

class GradeClassInfo(BaseModel):
    grades: list[Grade]

def parse_gradeclass(client, prompt):
    """Parse the grade class information

    Args:
        client (openai.OpenAI): OpenAI client
        prompt (str): usr course scheduling prompt

    Returns:
        list[list[str]]: a list of gradeclass constraints with format: [gradeDcode, classname]
    """
    grade_instruction = file_reader("../prompt_library/parse_gradeclass.txt")
    grade_instruction += "年级代号对应"
    grade_instruction += str(get_grade2gradeDcode())
    grade_instruction += "班级名称枚举"
    grade_instruction += str(get_unique_classnames())

    response = get_openai_response_structured(client, grade_instruction, prompt, GradeClassInfo)

    gradeclass_constraints = []
    for grade in response.grades:
        if grade.classes == None:
            gradeclass_constraints.append([grade.gradeDcode, None])
        else:
            for curr_class in grade.classes:
                gradeclass_constraints.append([grade.gradeDcode, curr_class.name])
    return pd.Series(gradeclass_constraints).drop_duplicates().tolist()

class Teacher(BaseModel):
    teachername: Optional[str]
    grade: Optional[Grade]
    coursename: Optional[str]

class TeacherInfo(BaseModel):
    teachers: list[Teacher]
    
def parse_teacher(client, prompt):
    """Parse the teacher information

    Args:
        client (openai.OpenAI): OpenAI client
        prompt (str): usr course scheduling prompt

    Returns:
        list[list[str]]: a list of teacher constraints with format: 
            [teachername, gradeDcode, coursename]
    """
    teacher_instruction = file_reader("../prompt_library/parse_teacher.txt")
    
    teacher_instruction += "以下是所有的教师人名："
    teacher_instruction += str(get_unique_teachers())
    teacher_instruction += "年级代号对应"
    teacher_instruction += str(get_grade2gradeDcode())

    response = get_openai_response_structured(client, teacher_instruction, prompt, TeacherInfo)

    teacher_constraints = []
    for teacher in response.teachers:
        if teacher.grade == None:
            gradeDcode = None
        else:
            gradeDcode = teacher.grade.gradeDcode
        teacher_constraints.append([teacher.teachername, gradeDcode, teacher.coursename])
    return pd.Series(teacher_constraints).drop_duplicates().tolist()

class Course(BaseModel):
    coursename: str
    gradeDcodes: Optional[list[str]]

class CourseInfo(BaseModel):
    courses: list[Course]

def parse_course(client, prompt):
    """Parse the course information

    Args:
        client (openai.OpenAI): OpenAI client
        prompt (str): usr course scheduling prompt

    Returns:
        list[list[str, list[str]]]: a list of course constraints with format: 
            [coursename, list[gradeDcode]] e.g. [["语文", ["J1", "J3"]]]
    """
    course_instruction = file_reader("../prompt_library/parse_course.txt")
    course_instruction += "以下是所有课程名称："
    course_instruction += str(get_unique_courses())
    course_instruction += "年级代号对应"
    course_instruction += str(get_grade2gradeDcode())

    response = get_openai_response_structured(client, course_instruction, prompt, CourseInfo)

    courses_constraints = []
    for course in response.courses:
        if course.gradeDcodes == None or len(course.gradeDcodes) == 0:
            courses_constraints.append([course.coursename, None])
        else:
            courses_constraints.append([course.coursename, course.gradeDcodes])
    return pd.Series(courses_constraints).drop_duplicates().tolist()

class MoveCourse(BaseModel):
    classInfo: Class
    courseInfo: Course

class MoveCourseInfo(BaseModel):
    moveCourses : list[MoveCourse]

def parse_Movecourse(client, prompt):
    """Parse the course information

    Args:
        client (openai.OpenAI): OpenAI client
        prompt (str): usr course scheduling prompt

    Returns:
        list[list[str, list[str]]]: a list of course constraints with format: 
            [coursename, list[gradeDcode]] e.g. [["语文", ["J1", "J3"]]]
    """
    course_instruction = file_reader("../prompt_library/parse_Movecourse.txt")
    course_instruction += "以下是所有课程名称："
    course_instruction += str(get_unique_courses())
    course_instruction += "年级代号对应"
    course_instruction += str(get_grade2gradeDcode())

    response = get_openai_response_structured(client, course_instruction, prompt, MoveCourseInfo)

    move_courses_constraints = []
    for moveCourse in response.moveCourses:
        move_courses_constraints.append([moveCourse.classInfo.gradeDcode, moveCourse.classInfo.name, moveCourse.courseInfo.coursename])
    return pd.Series(move_courses_constraints).drop_duplicates().tolist()
    

class PeriodDay(BaseModel):
    period: int
    dayOfWeek: int
    afternoon: bool

class PeriodDayInfo(BaseModel):
    perioddays : list[PeriodDay]

def parse_perioddays(client, prompt):
    """Parse the period and day information

    Args:
        client (openai.OpenAI): OpenAI Client
        prompt (str): user prompt

    Returns:
        list[dict]: a list of dictonaries with period and day information with format:
                    {"period": ..., "dayOfWeek": ...} 
    """
    file_content = file_reader_json(config.file_courseperiod)
    totalPeriod = file_content["data"]["totalPeriod"]
    lunchPeriod = file_content["data"]["lunchPeriod"]
    allow_lunchPeriod = file_content["data"]["allowLunchClass"]
    allow_saturdayClass = file_content["data"]["allowSaturdayClass"]
    allow_sundayClass = file_content["data"]["allowSundayClass"]
    weekdays = file_content["data"]["weekdays"]
    weekdays = list(map(int, weekdays))
    
    perioddays_instruction = file_reader("../prompt_library/parse_periodday.txt")
    perioddays_instruction += ("已知每天最多" + str(totalPeriod) + "节课。")
    response = get_openai_response_structured(client, perioddays_instruction, prompt, PeriodDayInfo)
    
    period_days = []
    for periodday in response.perioddays:
        if periodday.period in [99, -99, -1] or (not periodday.afternoon):
            period_days.append({
                "period" : periodday.period,
                "dayOfWeek" : periodday.dayOfWeek
            })
        else:
            if (periodday.period + lunchPeriod) <= totalPeriod:
                period_days.append({
                    "period" : periodday.period + lunchPeriod,
                    "dayOfWeek" : periodday.dayOfWeek
                })
            else:
                period_days.append({
                    "period" : periodday.period,
                    "dayOfWeek" : periodday.dayOfWeek
                })            
        if (period_days[-1]["period"] not in [-1, 99, -99]) and (period_days[-1]["period"] > totalPeriod):
            print("您排了第", period_days[-1]["period"], "节课，超出了您预设的每天", totalPeriod, "节限制。")
            exit(0)
        if period_days[-1]["period"] == lunchPeriod and (not allow_lunchPeriod):
            print("您已禁用在午餐时间（第", lunchPeriod, "时段）排课。")
            exit(0)
        if period_days[-1]["dayOfWeek"] == 6 and allow_saturdayClass:
            continue
        if period_days[-1]["dayOfWeek"] == 7 and allow_sundayClass:
            continue
        if (period_days[-1]["dayOfWeek"] not in weekdays) and period_days[-1]["dayOfWeek"] != -1:
            print("您试图在星期", period_days[-1]["dayOfWeek"], "排课，超出了您设定的工作日：", weekdays, "。")
            exit(0)
    empty_periodday = {
                    "period": -1,
                    "dayOfWeek": -1
                }
    if empty_periodday in period_days:
        return []
    return pd.Series(period_days).drop_duplicates().tolist()

def get_periodday_detailed(period_days):
    """Convert period day information to more detailed form for consecutive course

    Args:
        period_days (list[dict]): a list of dictionaries describing the period day information

    Returns:
        list[dict]: a detailed list of dictionaries describing the period day information
    """
    file_content = file_reader_json(config.file_courseperiod)
    totalPeriod = file_content["data"]["totalPeriod"]
    lunchPeriod = file_content["data"]["lunchPeriod"]
    allow_lunchPeriod = file_content["data"]["allowLunchClass"]
    weekdays = file_content["data"]["weekdays"]
    weekdays = list(map(int, weekdays))
    
    period_days_detailed = []
    for period_day in period_days:
        day = period_day["dayOfWeek"]
        period = period_day["period"]
        if day == -1:
            valid_days = weekdays
        else:
            valid_days = [day]
        if period == -1:
            valid_periods = list(range(1, totalPeriod+1))
            if allow_lunchPeriod == False:
                valid_periods.remove(lunchPeriod)
        elif period == 99:
            valid_periods = list(range(1, lunchPeriod))
        elif period == -99:
            valid_periods = list(range(lunchPeriod+1, totalPeriod + 1))
        else:
            valid_periods = [period]
        for valid_day in valid_days:
            for valid_period in valid_periods:
                period_days_detailed.append({
                    "period" : valid_period,
                    "dayOfWeek" : valid_day
                })
    return pd.Series(period_days_detailed).drop_duplicates().tolist()
    
    
class ScheduleLimits(BaseModel):
    limits: int
    maxlimits: Optional[int]

def parse_limits(client, prompt, type):
    """Parse the limits information

    Args:
        client (openai.OpenAI): OpenAI API
        prompt (str): user prompt
        type (str): the scheduling prompt type

    Returns:
        dict: a dictionary that shows the limit information in the prompt
    """
    limits_instruction = file_reader("../prompt_library/parse_limits.txt")
    limits_instruction += f"We know the the user prompt type is: {type}"

    response = get_openai_response_structured(client, limits_instruction, prompt, ScheduleLimits)
    
    if response.limits == response.maxlimits == -1:
        return {}

    answer = {
        "limits": response.limits,
        "maxlimits": response.maxlimits
    }
    return answer

class ConstraintType(BaseModel):
    type: str

def parse_constraint_type(client, prompt):
    """Get the "ContraintType" information of the prompt

    Args:
        client (openai.OpenAI): OpenAI API
        prompt (str): user prompt

    Returns:
        str: ConstraintType of the prompt
    """
    constraint_instruction = file_reader("../prompt_library/parse_constraint_type.txt")

    response = get_openai_response_structured(client, constraint_instruction, prompt, ConstraintType)
    return response.type

if __name__ == "__main__":

    # Get the API key from environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")

    # Get the user prompt
    user_prompt = input("请输入您的排课需求：")

    # Set the API key
    openai.api_key = config.openai_api_key

    # Initialize the OpenAI client with your API key
    client = openai.OpenAI(api_key=openai_api_key)
    response = parse_gradeclass(client, user_prompt)
    print(response)
    # response = parse_teacher(client, user_prompt)
    print("grade: ", response.grades[0].gradeDcode)