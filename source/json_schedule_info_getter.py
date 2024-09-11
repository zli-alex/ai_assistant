import pandas as pd
import config
from read_file import file_reader_json
from collections.abc import Iterable


# ------ Helper functions that ideally stays within this file ------ #

def recognize_none(val):
    if val == None:
        return True
    if isinstance(val, Iterable) and len(val) == 0:
        return True
    if val == "None":
        return True
    return False


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
            df = pd.concat([df, df_temp], ignore_index=True)
    return df


def df_expand_column(df, columns, prefix=False):
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
    file_content = file_reader_json(config.file_courseclass)
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
    file_content = file_reader_json(config.file_teacherinfo)
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
    file_content = file_reader_json(config.file_teacherinfo)
    if file_content["code"] == "SUCCESS":
        return file_content["data"]["projectId"]
    else:
        return None


def get_unique_courses():
    """Get Unique Courses

    Returns:
        list[str]: list of unique course names
    """
    if len(config.unique_courses) > 0:
        return config.unique_courses
    if len(config.df_courses) == 0:
        config.df_courses = get_courses_info(config.file_courseclass)
    config.unique_courses = config.df_courses["name"].unique().tolist()
    return config.unique_courses


def get_unique_teachers():
    """Get Unique Teachers

    Returns:
        list[str]: list of unique teacher names
    """
    if len(config.unique_teachers) > 0:
        return config.unique_teachers
    if len(config.df_teachers) == 0:
        config.df_teachers = get_teachers_info(config.file_teacherinfo)
    config.unique_teachers = config.df_teachers["teachername"].unique().tolist()
    return config.unique_teachers


def get_grade2gradeDcode():
    """Get gradename to gradeDcode dictionary

    Returns:
        dict: mapping from gradename to gradeDcode
    """
    if len(config.grade2gradeDcode) > 0:
        return config.grade2gradeDcode
    if len(config.df_classes) == 0:
        config.df_classes = get_classes_info(config.file_courseclass)

    for _, row in config.df_classes.iterrows():
        config.grade2gradeDcode[row["gradeName"]] = row["gradeDcode"]
    return config.grade2gradeDcode


def get_unique_classnames():
    """Get unique classnames

    Returns:
        list: unique classnames
    """
    if len(config.unique_classes) > 0:
        return config.unique_classes
    if len(config.df_classes) == 0:
        config.df_classes = get_classes_info(config.file_courseclass)
    config.unique_classes = config.df_classes["name"].unique().tolist()
    return config.unique_classes


def get_classes(gradeclass_constraints):
    """Get all classes with respect to input constraints

    Args:
        gradeclass_constraints (list[list[str]]):
            a list of constraints in format: list[gradeDcode, classname]

    Returns:
        list[dict]: a list of dictionaries describing courses
    """
    if len(config.df_classes) == 0:
        config.df_classes = get_classes_info(config.file_courseclass)
    answer = []
    for curr_gradeD, curr_class in gradeclass_constraints:
        if recognize_none(curr_class):
            df_curr = config.df_classes.loc[config.df_classes["gradeDcode"] == curr_gradeD]
        else:
            df_curr = config.df_classes.loc[
                (config.df_classes["gradeDcode"] == curr_gradeD) & (config.df_classes["name"] == curr_class)]
        if len(df_curr) == 0:
            print("您的班级数据库中不包含同时满足：年级为", curr_gradeD, "、班级为", curr_class, "的信息。")
            exit(0)
        for _, row in df_curr.iterrows():
            answer.append({
                "gradeName": row["gradeName"],
                "name": row["gradeName"] + row["name"],
                "alias": row["alias"],
                "uid": row["uid"],
                "type": row["type"]
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
    if len(config.df_teachers) == 0:
        config.df_teachers = get_teachers_info(config.file_teacherinfo)
    answer = []
    for name, gradeD, course in teacher_constraints:
        df_curr = config.df_teachers
        if not recognize_none(name):
            df_curr = df_curr.loc[df_curr["teachername"] == name]
        if not recognize_none(gradeD):
            df_curr = df_curr.loc[df_curr["gradeDecode"] == gradeD]
        if not recognize_none(course):
            df_curr = df_curr.loc[df_curr["coursename"] == course]
        if len(df_curr) == 0:
            print("您的教师数据库中不包含同时满足：教师名字为", name, "、年级为", gradeD, "、教授课程为", course,
                  "的信息。")
            exit(0)
        for _, row in df_curr.iterrows():
            answer.append({
                "uid": row["teacheruid"],
                "name": row["teachername"]
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
    if len(config.df_courses) == 0:
        config.df_courses = get_courses_info(config.file_courseclass)
    for course, gradeDcodeList in courses_constraints:
        df_curr = config.df_courses.loc[config.df_courses["name"] == course]
        if not recognize_none(gradeDcodeList):
            df_curr = df_curr.loc[df_curr["gradeDcode"].isin(gradeDcodeList)]
        if len(df_curr) == 0:
            print("您的学科课程数据库中不包含同时满足：课程为", course, "、年级为", gradeDcodeList, "的信息。")
            exit(0)
        for _, row in df_curr.iterrows():
            answer.append({
                "name": row["name"],
                "uid": row["uid"],
                "courseDcode": row["courseDcode"]
            })
    return pd.Series(answer).drop_duplicates().tolist()


def get_teachertimecluster(teacher_constraints, cluster_info = {}):
    """Function to generate teacher-time cluster information as special case

    Args:
        teacher_constraints (list[list[str]]): a list of teacher constraints in the following format:
                                                list[teachername, gradeDcode, coursename]
        cluster_info (dict): cluster parameter information

    Returns:
        list[dict]: a list of dictionaries summarizing course-teacher cluster information
    """
    if len(config.df_teachers) == 0:
        config.df_teachers = get_teachers_info(config.file_teacherinfo)
        
    df_answers = pd.DataFrame()  # Start with an empty DataFrame
    answer = []
    
    for name, gradeD, course in teacher_constraints:
        df_curr = config.df_teachers
        if not recognize_none(name):
            df_curr = df_curr.loc[df_curr["teachername"] == name]
        if not recognize_none(gradeD):
            df_curr = df_curr.loc[df_curr["gradeDecode"] == gradeD]
        if not recognize_none(course):
            df_curr = df_curr.loc[df_curr["coursename"] == course]
        
        if df_curr.empty:
            print(f"您的教师数据库中不包含同时满足：名字为 {name}、年级为 {gradeD}、教授课程为 {course} 的信息")
            exit(0)
        
        df_answers = pd.concat([df_answers, df_curr], ignore_index=True)
    
    if df_answers.empty:
        return []
    
    # Drop duplicates based on all relevant columns to ensure unique combinations
    df_answers = df_answers.drop_duplicates(subset=['teachername', 'gradeDecode', 'coursename', 'courseuid', 'teacheruid'])
    
    for teachername in df_answers['teachername'].unique():
        df_curr = df_answers.loc[df_answers["teachername"] == teachername]
        cluster_curr = {
            "courses": [],
            "teacher": {
                "uid": df_curr['teacheruid'].iloc[0],
                "name": teachername
            }
        }
        
        # Create a unique set of courses to avoid duplication
        unique_courses = set()
        
        for _, row in df_curr.iterrows():
            cluster_curr["courses"].append({
                "name": row['coursename'],
                "uid": row['courseuid'],
                "courseDcode": row["coursecourseDcode"],
                "gradeDcode": row["gradeDecode"],
                "checked": True
            })
        cluster_curr.update(cluster_info)
        answer.append(cluster_curr)
    return answer


def multi_course(courses_constraints):
    """
    Generate a structured output with multiple courses assigned as courseA and courseB.

    Args:
        courses_constraints (list[list[str]]):
            A list of constraints with format: list[coursename, list[gradeDcode]].
            Example: [["美术", ["J2"]], ["音乐", ["J2"]]]

    Returns:
        dict: A dictionary containing courseA and courseB assignments.
    """
    answer = []
    if config.df_courses.empty:
        config.df_courses = get_courses_info(config.file_courseclass)

    # Process each course constraint
    for course, gradeDcodeList in courses_constraints:
        df_curr = config.df_courses.loc[config.df_courses["name"] == course]
        if gradeDcodeList:
            df_curr = df_curr.loc[df_curr["gradeDcode"].isin(gradeDcodeList)]
        if df_curr.empty:
            raise ValueError(f"No matching courses found for {course} with gradeDcode {gradeDcodeList}")

        # Append matching courses to the answer list
        for _, row in df_curr.iterrows():
            answer.append({
                "name": row["name"],
                "uid": row["uid"],
                "courseDcode": row["courseDcode"]
            })

    # Determine courseA and courseB based on the number of courses found
    if len(answer) == 1:
        # If only one course, set it as both courseA and courseB
        courseA = courseB = answer[0]
    elif len(answer) >= 2:
        # If two courses, assign them to courseA and courseB
        courseA = answer[0]
        courseB = answer[1]
    else:
        raise ValueError("No valid courses found.")

    return {"courseA": courseA, "courseB": courseB}

if __name__ == "__main__":
    print(get_unique_teachers())
    print(get_unique_courses())
    # courses = get_courses_info()
    # print(courses.columns)
    # print(courses.head(5))
    # classes = get_classes_info()
    # print(classes.columns)
    # print(classes.head(5))
    # teachers = get_teachers_info()
    # print(teachers.columns)
    # print(teachers.head(5))
    # print(get_teachertimecluster([[None, 'J2', '数学']], {"fun" : "no class"}))
    exit()
