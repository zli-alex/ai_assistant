import pandas as pd
import os, json

def dicts2df(dicts, columns):
    df = pd.DataFrame({})
    for dict in dicts:
        temp = {}
        for column in columns:
            temp[column] = dict[column]
        df_temp = pd.DataFrame(temp)
        if len(df) == 0:
            df = df_temp
        else:
            df = pd.concat([df, df_temp], ignore_index= True)
    return df

def df_expand_column(df, columns, prefix = False):
    for column in columns:
        expanded = df[column].apply(pd.Series)
        if prefix:
            expanded = expanded.add_prefix(column)
        df = pd.concat([df.drop(columns=[column]), expanded], axis=1)
    return df

def get_courseslasses_info(filename, coursesclasses):
    file = open(filename)
    file_content = json.load(file)
    if file_content["code"] == "SUCCESS":
        df = dicts2df(file_content["data"], ["gradeDcode", coursesclasses])
        df = df_expand_column(df, [coursesclasses])
        return df
    else:
        return None

def get_courses_info(filename):
    return get_courseslasses_info(filename, "courses")

def get_classes_info(filename):
    return get_courseslasses_info(filename, "classes")

def get_unique_courses(filename):
    df = get_courses_info(filename)
    return list(df["name"].unique())

def get_teachers_info(filename):
    file = open(filename)
    file_content = json.load(file)
    if file_content["code"] == "SUCCESS":
        df = dicts2df(file_content["data"]["gradeTeacherClassList"], ["gradeDecode", "teacherClasses"])
        df = df_expand_column(df, ["teacherClasses"])
        df = df_expand_column(df, ["course", "teacher", "clazz"], True)
        df = df.loc[:, ~df.columns.duplicated()]
        return df
    else:
        return None

def get_project_id(filename):
    file = open(filename)
    file_content = json.load(file)
    if file_content["code"] == "SUCCESS":
        return file_content["data"]["projectId"]
    else:
        return None

def get_classes(filename, gradeclass_constraints):
    if len(gradeclass_constraints) == 0:
        return None
    df_classes = get_classes_info(filename)
    answer = []
    for curr_gradeD, curr_class in gradeclass_constraints:
        if curr_class == None:
            df_curr = df_classes.loc[df_classes["gradeDcode"] == curr_gradeD]
        else:
            df_curr = df_classes.loc[(df_classes["gradeDcode"] == curr_gradeD) & (df_classes["name"] == curr_class) ]
        for _, row in df_curr.iterrows():
            answer.append({
                "gradeName" : row["gradeName"],
                "name" : row["gradeName"] + row["name"],
                "alias": row["alias"],
                "uid" : row["uid"],
                "type" : row["type"]
            })
    return pd.Series(answer).drop_duplicates().tolist()

def get_teachers(filename, teacher_constraints):
    if len(teacher_constraints) == 0:
        return None
    df_teachers = get_teachers_info(filename)
    answer = []
    for name, gradeD, course in teacher_constraints:
        df_curr = df_teachers
        if name != None and name != "None":
            df_curr = df_curr.loc[df_curr["teachername"] == name]
        if gradeD != None and gradeD != "None":
            df_curr = df_curr.loc[df_curr["gradeDecode"] == gradeD]
        if course != None and course != "None":
            df_curr = df_curr.loc[df_curr["coursename"] == course]
        for _, row in df_curr.iterrows():
            answer.append({
                "uid" : row["teacheruid"],
                "name" : row["teachername"]
            })
    return pd.Series(answer).drop_duplicates().tolist()

def get_courses(filename, courses_constraints):
    answer = []
    df_courses = get_courses_info(filename)
    for course, gradeDodeList in courses_constraints:
        df_curr = df_courses.loc[df_courses["name"] == course]
        if gradeDodeList != None:
            df_curr = df_curr.loc[df_curr["gradeDcode"].isin(gradeDodeList)]
        if len(df_curr) == 0:
            answer.append({
                "name" : course,
                "uid" : "",
                "courseDcode" : "OTHER"
            })
        for _, row in df_curr.iterrows():
            answer.append({
                "name" : row["name"],
                "uid" : row["uid"],
                "courseDcode" : row["courseDcode"]
            })
    return pd.Series(answer).drop_duplicates().tolist()

    
if __name__ == "__main__":
    courses = get_courses_info("./inputs/课程和班级信息.json")
    print(courses.head(5))
    # classes = get_classes_info("./inputs/课程和班级信息.json")
    # print(classes.columns)
    # print(classes.head(5))
    teachers = get_teachers_info("./inputs/教师任课信息.json")
    print(teachers.columns)
    print(len(teachers))
    print(teachers["teachername"].unique())
    exit()