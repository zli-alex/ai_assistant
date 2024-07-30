# ai_assistant

## prompt params
| Assistant    | file | temp |
| -------- | ------- |  ------- |
| filter  | n/a    | 0.01 |
| summary | n/a     | 0.1 |
| classify    | n/a    | 0.01 |
| *2json | file search: 课程班级+教师任科 | 0.01|

## TODO's:
- helper function:
  - create assistant (pzh)
    - input:
      - txt file
      - client
      - input file
    - output: assistant_id
  - delete assistants (cyd)
    - input:
      - a list of assistant id's
  - ? better return json?(cyd)
- tests (lzf)
  - test cases
    - all use cases + paraphrase