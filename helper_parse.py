from pydantic import BaseModel
import openai
from typing import Optional
from helpers import file_reader, get_openai_response_binary, get_openai_response_structured
from dotenv import load_dotenv
import os
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
    instruction = "请判断以下用户提示词是否人名,有提及请回答True，并返回。\
                否则请判断用户提示词是否包含“教师”等教职职称，有请回答True。如果都没有提及请回答False。\
                用户提示词：李梅数学课在早上第一节。 请回答：True。用户提示词：美术排在早上第四节。 请回答：False。"
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
                体活、美术等的初中学科名称或者初中课程名称。有请回答True，没有请回答False。\
                用户提示词：美术排在早上第四节。 请回答：True。用户提示词：初三周四第九节不排。 请回答：False。"
    response = get_openai_response_binary(client, instruction, prompt)
    return response

class Class(BaseModel):
    gradeName: str
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
    grade_instruction = file_reader("./prompt_library/parse_gradeclass.txt")

    response = get_openai_response_structured(client, grade_instruction, prompt, GradeClassInfo)

    gradeclass_constraints = []
    for grade in response.grades:
        if grade.classes == None:
            gradeclass_constraints.append([grade.gradeDcode, None])
        else:
            for curr_class in grade.classes:
                gradeclass_constraints.append([grade.gradeDcode, curr_class.name])
    return gradeclass_constraints

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
    teacher_instruction = file_reader("./prompt_library/parse_teacher.txt")

    response = get_openai_response_structured(client, teacher_instruction, prompt, TeacherInfo)

    teacher_constraints = []
    for teacher in response.teachers:
        if teacher.grade == None:
            gradeDcode = None
        else:
            gradeDcode = teacher.grade.gradeDcode
        teacher_constraints.append([teacher.teachername, gradeDcode, teacher.coursename])
    return teacher_constraints

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
    course_instruction = file_reader("./prompt_library/parse_course.txt")

    response = get_openai_response_structured(client, course_instruction, prompt, CourseInfo)

    courses_constraints = []
    for course in response.courses:
        print(course)
        if course.gradeDcodes == None or len(course.gradeDcodes) == 0:
            courses_constraints.append([course.coursename, None])
        else:
            courses_constraints.append([course.coursename, course.gradeDcodes])
    return courses_constraints

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    # Get the API key from environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")

    # Get the user prompt
    user_prompt = input("请输入您的排课需求：")

    # Set the API key
    openai.api_key = openai_api_key

    # Initialize the OpenAI client with your API key
    client = openai.OpenAI(api_key=openai_api_key)
    response = parse_gradeclass(client, user_prompt)
    print(response)
    # response = parse_teacher(client, user_prompt)
    print("grade: ", response.grades[0].gradeDcode)