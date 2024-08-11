from pydantic import BaseModel
import openai
from typing import Optional
from helpers import file_reader
from dotenv import load_dotenv
import os
# For structured output, need python 3.12

def relevance_gradeclass(client, prompt):
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "请判断以下用户提示词是否有提及年级或者班级信息。有提及请回答True，没有提及请回答False。用户提示词：初二3班李梅数学课在早上第四节。 请回答：True。用户提示词：张华的物理课只能上每天第九节。 请回答：False。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def relevance_teacher(client, prompt):
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "请判断以下用户提示词是否人名,有提及请回答True，并返回。否则请判断用户提示词是否包含“教师”等教职职称，有请回答True。如果都没有提及请回答False。用户提示词：李梅数学课在早上第一节。 请回答：True。用户提示词：美术排在早上第四节。 请回答：False。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def relevance_course(client, prompt):
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "请判断以下用户提示词中是否有包括但是不仅限于语文、体活、美术等的初中学科名称或者初中课程名称。有请回答True，没有请回答False。用户提示词：美术排在早上第四节。 请回答：True。用户提示词：初三周四第九节不排。 请回答：False。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

class Class(BaseModel):
    gradeName: str
    name: str

class Grade(BaseModel):
    gradeDcode: str
    classes: Optional[list[Class]]

class GradeClassInfo(BaseModel):
    grades: list[Grade]

def parse_gradeclass(client, prompt):

    grade_instruction = file_reader("./prompt_library/parse_gradeclass.txt")

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": grade_instruction},
            {"role": "user", "content": prompt}
        ],
        response_format=GradeClassInfo,
        temperature=0.01
    )

    response = completion.choices[0].message.parsed
    return response

class Teacher(BaseModel):
    teachername: Optional[str]
    grade: Optional[Grade]
    coursename: Optional[str]

class TeacherInfo(BaseModel):
    teachers: list[Teacher]
    
def parse_teacher(client, prompt):

    teacher_instruction = file_reader("./prompt_library/parse_teacher.txt")

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": teacher_instruction},
            {"role": "user", "content": prompt}
        ],
        response_format=TeacherInfo,
        temperature=0.01
    )

    response = completion.choices[0].message.parsed
    return response

class Course(BaseModel):
    coursename: str
    gradeDcode: Optional[list[str]]

class CourseInfo(BaseModel):
    courses: list[Course]

def parse_course(client, prompt):

    course_instruction = file_reader("./prompt_library/parse_course.txt")

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": course_instruction},
            {"role": "user", "content": prompt}
        ],
        response_format=CourseInfo,
        temperature=0.01
    )

    response = completion.choices[0].message.parsed
    return response

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