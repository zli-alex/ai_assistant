import pandas as pd
import json
import config

# ------ Helper functions that ideally stays within this file ------ #


def dicts2df(dicts, columns):
    """Transform from dictionaries (rows) to pandas df

    Args:
        dicts (list[dict]): a list of dictionaries
        columns (list[str]): a list of desired column names

    Returns:
        pd.DataFrame: the desired dataframe
    """
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
    """Expand a column of dicts to several columns

    Args:
        df (pd.DataFrame): original dataframe
        columns (list[str]): a list of column names that is to be expanded
        prefix (bool, optional): whether a column name prefix is to be added. Defaults to False.

    Returns:
        _type_: _description_
    """
    for column in columns:
        expanded = df[column].apply(pd.Series)
        if prefix:
            expanded = expanded.add_prefix(column)
        df = pd.concat([df.drop(columns=[column]), expanded], axis=1)
    return df

def get_courseslasses_info(filename, coursesclasses):
    """Read in the courseclass information

    Args:
        filename (str): path to course-class info json file
        coursesclasses (str): either "courses" or "classes", and returns that block of data

    Returns:
        pd.DataFrame: a df of either courses or classes
    """
    file = open(filename)
    file_content = json.load(file)
    if file_content["code"] == "SUCCESS":
        df = dicts2df(file_content["data"], ["gradeDcode", coursesclasses])
        df = df_expand_column(df, [coursesclasses])
        return df
    else:
        return None

def get_courses_info(filename):
    """Get courses dataframe with columns: ['gradeDcode', 'name', 'uid', 'courseDcode']

    Args:
        filename (str): path to course-class json

    Returns:
        pd.DataFrame: pd df of courses
    """
    return get_courseslasses_info(filename, "courses")


def get_classes_info(filename):
    """Get classes dataframe with columns:
        ['gradeDcode', 'gradeName', 'name', 'alias', 'uid', 'type']

    Args:
        filename (str): path to course-class json

    Returns:
        pd.DataFrame: pd df of classes
    """
    return get_courseslasses_info(filename, "classes")


def get_teachers_info(filename):
    """Get teachers dataframe with columns:
        ['gradeDecode', 'id', 'teachType', 'teacherUserName', 'courseRank', 'courseHour', 
        'evenOddHours', 'isMultiClass', 'code', 'coursename', 'courseuid', 'coursecourseDcode', 
        'teachername', 'teacheruid', 'clazzname', 'clazzuid']

    Args:
        filename (str): path to file

    Returns:
        pd.DataFrame: pd df of teachers dataframe
    """
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

# ------ User-friendly functions below ------ #

def get_project_id():
    """Get project ID

    Returns:
        str: Project ID
    """
    file = open(config.file_teacherinfo)
    file_content = json.load(file)
    if file_content["code"] == "SUCCESS":
        return file_content["data"]["projectId"]
    else:
        return None

def get_unique_courses():
    """Get Unique Courses

    Returns:
        list[str]: list of unique course names
    """
    df = get_courses_info(config.file_courseclass)
    return df["name"].unique().to_list()

def get_unique_teachers():
    """Get Unique Teachers

    Returns:
        list[str]: list of unique teacher names
    """
    df = get_teachers_info(config.file_teacherinfo)
    return df["teachername"].unique().to_list()


def get_classes(gradeclass_constraints):
    """Get all classes with respect to input constraints

    Args:
        gradeclass_constraints (list[list[str]]): 
            a list of constraints in format: list[gradeDcode, classname]

    Returns:
        list[dict]: a list of dictionaries describing courses
    """
    if len(gradeclass_constraints) == 0:
        return None
    df_classes = get_classes_info(config.file_courseclass)
    answer = []
    for curr_gradeD, curr_class in gradeclass_constraints:
        if curr_class == None:
            df_curr = df_classes.loc[df_classes["gradeDcode"] == curr_gradeD]
        else:
            df_curr = df_classes.loc[(df_classes["gradeDcode"] == curr_gradeD) & (df_classes["name"] == curr_class)]
        for _, row in df_curr.iterrows():
            answer.append({
                "gradeName" : row["gradeName"],
                "name" : row["gradeName"] + row["name"],
                "alias": row["alias"],
                "uid" : row["uid"],
                "type" : row["type"]
            })
    return pd.Series(answer).drop_duplicates().tolist()


def get_teachers(teacher_constraints):
    """Get all teachers with respect to input constraints

    Args:
        teacher_constraints (list[list[str]]):
            a list of constraints in format: list[teachername, gradeDcode, coursename]

    Returns:
        list[dict]: a list of dictionaries describing teachers
    """
    if len(teacher_constraints) == 0:
        return None
    df_teachers = get_teachers_info(config.file_teacherinfo)
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


def get_courses(courses_constraints):
    """Get all courses with respect to given constraints

    Args:
        courses_constraints (list[list[str]]): 
            a list of constraints with format: list[coursename, list[gradeDcode]]
            example: [["语文", ["J1", "J3"]]]

    Returns:
        list[dict]: a list of dictionaries describing courses
    """
    answer = []
    df_courses = get_courses_info(config.file_courseclass)
    for course, gradeDcodeList in courses_constraints:
        df_curr = df_courses.loc[df_courses["name"] == course]
        if gradeDcodeList != None:
            df_curr = df_curr.loc[df_curr["gradeDcode"].isin(gradeDcodeList)]
        for _, row in df_curr.iterrows():
            answer.append({
                "name" : row["name"],
                "uid" : row["uid"],
                "courseDcode" : row["courseDcode"]
            })
    return pd.Series(answer).drop_duplicates().tolist()

if __name__ == "__main__":
    courses = get_courses_info()
    print(courses.columns)
    print(courses.head(5))
    classes = get_classes_info()
    print(classes.columns)
    print(classes.head(5))
    teachers = get_teachers_info()
    print(teachers.columns)
    print(teachers.head(5))
    exit()