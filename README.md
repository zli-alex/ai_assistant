# ai_assistant

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
- 8/8: everyone try `COURSETIME` and `TEACHERTIME`
- 8/10: mass produce other types
  - pzh: consec/ c2c/ coursedaylimit/ cperiodlimit
  - cyd: csametimelimit/ evenoddlink/ movecourse/ teacherdaylimit
  - lzf: ...