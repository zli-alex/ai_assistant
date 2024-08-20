# ai_assistant

## Dependencies:

python 3.12.5

pandas  2.2.2

openai 1.40.1

dotenv 

pydantic 2.8.2

## Usage

To get started, please open `config.py` file and enter your OpenAI API Key:
```python
openai_api_key = "<Please_enter_your_OpenAIKey_here>"
```
Up to your demand, you can also change the input json information files, model name and temperature there.

Before run, prepare your course scheduling information and put it in `inputs/input_info.json`
```bash
{
    "input_info" : "<Your_course_scheduling_information_here>"
}
```

And then, you can run:
```
python3 schedule_chatbot.py
```

And then, you would enter course scheduling information in chinese when prompted:
```
请输入您的排课需求：<您的需求>

```

## TODO's:
- [x] config file
- [x] switch to pandas
  - get_courses_info: columns: ['gradeDcode', 'name', 'uid', 'courseDcode']
  - get_classes_info: columns: ['gradeDcode', 'gradeName', 'name', 'alias', 'uid', 'type']
  - get_teachers_info: columns: ['gradeDecode', 'id', 'teachType', 'teacherUserName', 'courseRank',
       'courseHour', 'evenOddHours', 'isMultiClass', 'code', 'coursename',
       'courseuid', 'coursecourseDcode', **'teachername'**, 'teacheruid',
       'clazzname', 'clazzuid']
- [x] pass teacher names to openai (lzf)
  - if teacher DNE
- [x] pass courses names to openai (lzf)
  - if coureses DNE
- [x] structured output if we demand True/False
- [ ] special cases:
  - [x] CONSECUTIVECOURSE: acourse & bcourse (cyd)
  - [x] COURSE2COURSE: prev. course & next course (cyd)
  - [x] EVENODDLINK: courseA & courseB (cyd)
  - [ ] TEACHERTIMEMUTEX: ateacher acourses & bteacher bcourses (pzh)
  - [x] TEACHERTIMECLUSTER: [{courses: ... , teacher: ...}] (lzf)
  - [ ] MOVECOURSE: [pair<class, courses>] (pzh)
- [x] 上午下午 (lzf)
  - 99上午；-99下午
  - 超出课程设定
- [x] other special flags (lzf)
- [ ] testing