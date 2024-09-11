import pandas as pd

openai_api_key = "<your_openai_key_here>"
model_name = "gpt-4o-mini"
model_temp = 0.01
file_input = "../inputs/input_info.json"
file_output = "../output_list.json"
file_courseclass = "../inputs/courseclass_info.json"
file_courseperiod = "../inputs/courseperiod_info.json"
file_teacherinfo = "../inputs/teacher_info.json"

# ------ Please do not change the code beklow ------ #

def init():
    global df_courses
    df_courses = pd.DataFrame({})
    global df_teachers
    df_teachers = pd.DataFrame({})
    global df_classes
    df_classes = pd.DataFrame({})
    global unique_teachers
    unique_teachers = []
    global unique_courses
    unique_courses = []
    global grade2gradeDcode
    grade2gradeDcode = {}
    global unique_classes
    unique_classes = []