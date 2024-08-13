# ai_assistant

## Dependencies:

python 3.12.5

pandas  2.2.2

openai 1.40.1

dotenv 

pydantic 2.8.2

## Usage

To use, please create a `.env` file in root directory and write your OpenAI API key with format:
```.env
OPENAI_API_KEY="<your_api_key>"
```

To run, enter the following code in terminal:
```bash
python3 ./prompt2json.py
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
- [ ] pass teacher names to openai (lzf)
  - if teacher DNE
- [ ] pass courses names to openai (lzf)
  - if coureses DNE
- [x] structured output if we demand True/False
- [ ] special cases:
  - [ ] CONSECUTIVECOURSE: acourse & bcourse (cyd)
  - [ ] COURSE2COURSE: prev. course & next course (cyd)
  - [ ] EVENODDLINK: courseA & courseB (cyd)
  - [ ] TEACHERTIMEMUTEX: ateacher acourses & bteacher bcourses (pzh)
  - [ ] TEACHERTIMECLUSTER: [{courses: ... , teacher: ...}] (lzf)
  - [ ] MOVECOURSE: [pair<class, courses>] (pzh)
- [ ] 上午下午等：special flags (lzf)
  - 99上午；-99下午
- [ ] testing