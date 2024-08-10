import json 
 
teacher_filepath = 'inputs/教师任课信息.json'
course_filepath = 'inputs/课程和班级信息.json'


def get_class(grade, classname):
    class_list = []
    file = open(course_filepath, "r", encoding='utf-8')
    class_object = json.loads(file.read())
    for data in class_object['data']:
        for clas in data['classes']:
            if grade is not None and classname is None:
                if clas['gradeName'] == grade:
                    class_list.append(clas)
            else:
                if clas['name'] == classname and clas['gradeName'] == grade:
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
    return course_list

        

def get_teacher(name, grade, subject):
    teacher_list = []
    file = open(teacher_filepath, "r", encoding='utf-8')
    teacher_object = json.load(file)
    for data in teacher_object['data']['gradeTeacherClassList']:
        for teacher_class in data['teacherClasses']:
            if name != None:
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
    return teacher_list

      