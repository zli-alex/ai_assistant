import json 
import pandas as pd
 
teacher_filepath = 'inputs/教师任课信息.json'
course_filepath = 'inputs/课程和班级信息.json'


def get_class(grade, classname):
    class_list = []
    file = open(course_filepath, "r", encoding='utf-8')
    class_object = json.loads(file.read())
    for data in class_object.get('data', []):
        if grade is not None and classname is None:
            if data.get('gradeDcode') == grade:
                class_list.extend(data.get('classes', []))
        elif grade is not None and classname is not None:
            if data.get('gradeDcode') == grade:
                for clas in data.get('classes', []):
                    if clas.get('name') == classname:
                        class_list.append(clas)
    
    return class_list

def get_course(grade, subject):
    course_list = []
    file = open(course_filepath, "r", encoding='utf-8')
    class_object = json.loads(file.read())
    
    for data in class_object['data']:
        # Ensure we use the correct key 'gradeDcode'
        if grade is not None and subject is None:
            if grade == data['gradeDcode']:
                for course in data['courses']:
                    course_list.append(course)
        elif grade is None and subject is not None:
            for course in data['courses']:
                if course['name'] == subject:
                    course_list.append(course)
        elif grade is not None and subject is not None:
            if grade == data['gradeDcode']:
                for course in data['courses']:
                    if course['name'] == subject:
                        course_list.append(course)
    if len(course_list) == 0:
        course_list = [{
            "name" : str(subject) + str(grade),
            "uid" : "",
            "courseDcode" : "OTHER_UNFOUND"
        }]
    return course_list

        

def get_teacher(name, grade, subject):
    teacher_list = []
    file = open(teacher_filepath, "r", encoding='utf-8')
    teacher_object = json.load(file)
    for data in teacher_object['data']['gradeTeacherClassList']:
        for teacher_class in data['teacherClasses']:
            if name != None and name != "None":
                teacher = teacher_class.get('teacher', {}) 
                if teacher['name'] == name:
                    teacher_list.append(teacher)
            elif grade != None and subject != None:
                if teacher_class['gradeDecode'] == grade and teacher_class['course']['name'] == subject:
                    teacher_list.append(teacher_class.get('teacher', {}))
            elif grade != None:
                if teacher_class['gradeDecode'] == grade:
                    teacher_list.append(teacher_class.get('teacher', {}))
            elif subject != None:
                if teacher_class['course']['name'] == subject:
                    teacher_list.append(teacher_class.get('teacher', {}))
    return pd.Series(teacher_list).drop_duplicates().tolist()

if __name__ == "__main__":
    print(get_teacher("None", "J1", '语文'))